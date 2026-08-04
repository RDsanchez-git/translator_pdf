# HITO_0.4.4_REGRESSION_ARCHITECTURE_AUDIT.md
## Integration Test Architecture, Recovery, Mocks & Boundary Forensic Audit — Reporte Consolidado Final

* **Estado:** FROZEN / CONGELADO (Dimensión Integration Tests)
* **Fecha de Emisión:** 2026-07-27
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.4
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Auditoría analítica y forense estricta basada en la inspección del 100% de la suite de integración (`tests/integration/`, 18 archivos). Cero mutaciones en código productivo. Disposición diferida al Hito 0.5 (`UNASSESSED`).

---

## 1. PROPÓSITO Y ALCANCE

El **Sub-hito 0.4.4 (Dimensión Integration)** audita la efectividad real, la profundidad de cobertura y la validez de las barreras de seguridad en la capa de integración. Examina la capacidad de la suite para detectar regresiones estructurales, fallos de concurrencia, corrupción de estados en la base de datos (FSM), intercepción de errores en salidas de LLM y desviaciones en la ingesta física de documentos.

---

## 2. REGISTRO DE EVIDENCIA FORENSE DE INTEGRACIÓN (E-0.4-301 a E-0.4-310)

### Evidencia E-0.4-301: Ingesta Física Real con Adaptación en Vuelo (Deuda de Taxonomía)
* **Archivo Fuente:** `tests/integration/test_real_paper.py`
* **Análisis Forense:** Se confirma que la suite **SÍ ejecuta la extracción sobre binarios PDF reales** llamando a `parse_pdf()` contra `sample_3_pages.pdf`. Sin embargo, el test inyecta un *monkey-patch* (`custom_ast_node_factory`) para convertir al vuelo la taxonomía Legacy V1 (`"EQUATION"`, `"TABLE"`) hacia `ContentNodeType` V2, evitando que `ASTValidator` falle.

---

### Evidencia E-0.4-302: Tautología en Pruebas Golden Parser (`GAP-0.4-09`)
* **Archivo Fuente:** `tests/integration/test_golden_parser.py`
* **Análisis Forense:** La prueba carga la huella congelada en disco, pero inmediatamente ejecuta `expected_fingerprint = current_fingerprint`. Esta asignación anula el oráculo de control y fuerza una aserción idéntica (`A == A`), haciendo que el test sea incapaz de detectar regresiones en el AST extraído.

---

### Evidencia E-0.4-303: Boundary & Contract Test de Adaptador PDF
* **Archivo Fuente:** `tests/integration/test_real_parser_pipeline.py`
* **Análisis Forense:** El test no analiza el PDF físico. Reemplaza el método `parse` de `PdfParserAdapter` mediante `patch.object` e inyecta una lista estática de 4 nodos mock. Actúa como un test de frontera de consumidor, no como una prueba de ingesta binaria.

---

### Evidencia E-0.4-304: Persistencia y Ciclo de Vida de Recuperación ante Fallos (FSM)
* **Archivos Fuente:** `tests/integration/test_recovery_flow.py`, `tests/integration/test_pipeline_orchestration.py`
* **Análisis Forense:** 
  * `test_recovery_flow.py` opera sobre una base de datos SQLite real en disco (`test_fsm.db`). Valida la detección de trabajos colgados por el `AbandonedProcessWatchdog` (`PROCESSING` $\rightarrow$ `STALLED`) y su rescate vía `OnDemandResumeManager`.
  * `test_pipeline_orchestration.py` ejecuta el `TranslationPipeline.execute()` real utilizando el Composition Root y SQLite en memoria, garantizando las transiciones del `TranslationJob` de `PENDING` a `COMPLETED`.

---

### Evidencia E-0.4-305: Concurrencia y Seguridad Asíncrona Bajo Carga
* **Archivo Fuente:** `tests/integration/test_healing_concurrency.py`
* **Análisis Forense:** Dispara **100 corrutinas concurrentes que registran 50,000 eventos** sobre `HealingTelemetryRegistry`, certificando la ausencia de condiciones de carrera y la exactitud en el cálculo incremental $O(1)$ de métricas de latencia y tasa de *rollback*.

---

### Evidencia E-0.4-306: Protección de Regresión Criptográfica por Snapshot en Empaquetado
* **Archivo Fuente:** `tests/integration/test_chunker_snapshot.py`
* **Análisis Forense:** Carga un AST de referencia y ejecuta `build_semantic_chunks_as_units()`. Compara el resultado nodo por nodo contra el archivo oráculo `sample_chunks.json`, validando campos críticos como `payload_sha256`, `target_payload` y `context_id`. Es una barrera de regresión determinista real.

---

### Evidencia E-0.4-307: Intercepción Dinámica de Respuestas Malformadas del LLM
* **Archivo Fuente:** `tests/integration/test_validation_integration.py`
* **Análisis Forense:** Mediante `StaticMockProvider`, inyecta respuestas con fallos deliberados (llaves LaTeX desbalanceadas, bloques Markdown indeseados, eliminación de DOIs) y comprueba que `AsyncDispatcher` e `ValidationPipeline` cancelen el avance del paquete (`outcome.is_success is False`).

---

### Evidencia E-0.4-308: Verificación Directa de Transporte de Red
* **Archivo Fuente:** `tests/integration/test_embedding_smoke.py`
* **Análisis Forense:** Si detecta la variable de entorno `GROQ_API_KEY`, ejecuta una llamada de red asíncrona real contra la API remota de Groq utilizando `OpenAICompatibleDialect`. Permite certificar el stack de transporte HTTP en entornos de integración.

---

### Evidencia E-0.4-309: Pruebas Controladas de Componentes ("Walking Skeleton" & FinOps)
* **Archivos Fuente:** `tests/integration/test_e2e_walking_skeleton.py`, `tests/integration/test_real_e2e.py`, `tests/integration/test_translation_layer.py`
* **Análisis Forense:** 
  * `test_e2e_walking_skeleton.py` opera sobre una base de datos SQLite real de caché en disco (`e2e_cache_real.db`), validando la reentrabilidad de caché ante *Hits* y *Misses*.
  * `test_real_e2e.py` simula la ejecución parcheando `pipeline.execute()`, validando el cálculo de costes FinOps en lugar de la orquestación del pipeline.

---

### Evidencia E-0.4-310: Inspección Post-Ensamblado y Vectores Sintéticos
* **Archivos Fuente:** `tests/integration/test_translation_semantics.py`, `tests/integration/test_translation_structure.py`, `tests/integration/test_translation_technical.py`
* **Análisis Forense:** 
  * `test_translation_semantics.py` utiliza un vector sintético constante (`[0.5] * 10`), actuando como un *scaffold* de prueba más que como un test semántico activo.
  * `test_translation_structure.py` y `test_translation_technical.py` utilizan `FakeChunker` y `FakeDispatcher` para validar la precisión del `MarkdownInspector` y el balance de sintaxis TeX.

---

## 3. TAXONOMÍA Y MATRIZ DE AUDITORÍA FORENSE (`tests/integration/`)

```text
[ TAXONOMÍA DE LA SUITE DE INTEGRACIÓN ]

1. REAL INTEGRATION (I/O & Componentes Reales):
   ├── test_real_paper.py (PDF Físico + ASTValidator)
   ├── test_recovery_flow.py (FSM State Machine + SQLite en disco)
   ├── test_validation_integration.py (Dispatcher + Validation Pipeline Filters)
   ├── test_chunker_snapshot.py (AST -> TranslationUnit SHA-256 Snapshots)
   └── test_healing_concurrency.py (Async-Safety, 50k Eventos)

2. BOUNDARY & CONTRACT TESTS (Cumplimiento de Interfaces):
   ├── test_real_parser_pipeline.py (PdfParserAdapter Customer Contract)
   ├── test_benchmark_orchestration_integration.py (OCP en SequentialBenchmarkOrchestrator)
   └── test_cli_router.py (Argument Parsing & Routing)

3. CONTROLLED / GOLDEN INTEGRATION (Zero-Cost Pipelines):
   ├── test_e2e_walking_skeleton.py (Caché SQLite Real + FakeLLM)
   ├── test_pipeline_orchestration.py (FSM SQLite Memory + Parser Mock)
   ├── test_real_e2e.py (FinOps Cost Validation + Pipeline Mock)
   ├── test_translation_layer.py (Dispatcher Order + Assembler Contract)
   ├── test_translation_structure.py (MarkdownInspector + Golden Snapshot)
   ├── test_translation_technical.py (TeX Token Inspector + Golden Snapshot)
   └── test_translation_semantics.py (Cosine Math Scaffold + Vector Mock)

4. SMOKE TESTS (Conectividad Opcional Externa):
   └── test_embedding_smoke.py (Llamada HTTP a Groq con API Key)

5. DEFECTIVE TESTS (Tautología / Falso Positivo):
   └── test_golden_parser.py (GAP-0.4-09: Tautología A == A)
```

| Archivo de Prueba | Categoría Arquitectónica | I/O Físico Real | Uso de Mocks / Stubs | Garantía Real Provista |
| :--- | :--- | :---: | :---: | :--- |
| `test_real_paper.py` | Real Integration | **SÍ** (PDF en disco) | Parcial (Traductor V1->V2) | **Alta:** Ingesta física real por PyMuPDF y control de calidad del AST. |
| `test_recovery_flow.py` | Real Integration | **SÍ** (SQLite en disco) | Parcial | **Alta:** Recuperación tras caídas, watchdog y reanudación de estado. |
| `test_validation_integration.py` | Real Integration | NO (Memoria) | Parcial (LLM Mock) | **Alta:** Intercepción de respuestas malformadas (LaTeX/MD). |
| `test_chunker_snapshot.py` | Real Integration | **SÍ** (JSON en disco) | **CERO** | **Alta:** Invariabilidad de `TranslationUnit` e identidad SHA-256. |
| `test_healing_concurrency.py` | Real Integration | NO (Memoria) | **CERO** | **Alta:** Seguridad en corrutinas asíncronas bajo 50,000 eventos. |
| `test_golden_parser.py` | Defective Test | NO | **TOTAL (Tautológico)** | **NULA (`GAP-0.4-09`):** Sobreescribe el oráculo y miquea el parser. |
| `test_real_parser_pipeline.py` | Boundary / Contract | NO | **TOTAL** | **Media:** Valida el contrato del consumidor sobre el adaptador. |
| `test_pipeline_orchestration.py` | Controlled Integration | **SÍ** (SQLite memory) | Parcial (Parser Mock) | **Alta:** Valida transiciones FSM y ciclo de vida del Job. |
| `test_healing_e2e_telemetry.py` | Controlled Integration | NO (Memoria) | Parcial | **Alta:** Mecanismo de rollback al texto original ante fallos. |
| `test_embedding_smoke.py` | Smoke Test | **SÍ** (API remota) | Condicional (API Key) | **Alta:** Conectividad física de red y dialecto OpenAI. |
| `test_e2e_walking_skeleton.py` | Controlled Integration | **SÍ** (SQLite en disco) | Parcial (LLM Mock) | **Media/Alta:** Reentrabilidad de caché SQLite en disco. |
| `test_real_e2e.py` | Controlled Integration | NO (Memoria) | ALTO (LLM/Pipeline Mock) | **Media:** Cálculo de costes y consumo de tokens. |
| `test_translation_layer.py` | Controlled Integration | NO (Memoria) | ALTO (LLM Mock) | **Media:** Preservación de orden de chunks hacia el ensamblador. |
| `test_translation_semantics.py` | Controlled Integration | NO (Memoria) | ALTO (Vector Mock) | **Baja:** Scaffold matemático de la similitud del coseno. |
| `test_translation_structure.py` | Controlled Integration | NO (Memoria) | ALTO (Fake Dispatcher) | **Media:** Expresiones regulares del `MarkdownInspector`. |
| `test_translation_technical.py` | Controlled Integration | NO (Memoria) | ALTO (Fake Dispatcher) | **Media:** Extracción de etiquetas, citas y balance de sintaxis TeX. |
| `test_benchmark_orchestration` | Boundary / Contract | NO (Memoria) | ALTO | **Media:** Cumplimiento del principio OCP en el benchmark. |
| `test_cli_router.py` | Boundary / Contract | NO (Memoria) | ALTO | **Media:** Enrutamiento de subcomandos CLI. |

---

## 4. EVALUACIÓN DE CONFIABILIDAD Y RECOMENDACIONES FUTURAS

### 4.1 DIAGNÓSTICO DE ALCANCE Y CONFIABILIDAD REAL

1. **FSM, Persistencia y Resiliencia:** **Alta confianza en el happy-path de recuperación y reanudación; cobertura todavía no equivalente a certificación exhaustiva de resiliencia.**
   Garantizado por `test_recovery_flow.py` y `test_pipeline_orchestration.py`. La persistencia transaccional SQLite y la recuperación de procesos colgados están plenamente certificadas.
2. **Intercepción de Fallos y Filtros:** **Alta confianza para los vectores de fallo explícitamente cubiertos.**
   Garantizado por `test_validation_integration.py` y `test_healing_e2e_telemetry.py`. Los errores de formato TeX/MD en las respuestas del LLM son bloqueados y replegados exitosamente.
3. **Ingesta Física y Extracción de PDFs:** **PARCIALMENTE CONFIABLE / CON DEUDA.**
   `test_real_paper.py` certifica el funcionamiento del motor de PyMuPDF, pero expone que la traducción de la taxonomía V1 hacia V2 ocurre mediante un *monkey-patch* en el test y no en el parser productivo.
4. **Regresión Estructural de AST:** **VULNERABLE (`GAP-0.4-09`).**
   La prueba `test_golden_parser.py` posee un vicio tautológico que invalida la comparación contra el oráculo congelado en disco.

---

### 4.2 RECOMENDACIONES ARQUITECTÓNICAS DIFERIDAS (NO BLOQUEANTES)

#### REC-0.4.4-01 — Eliminar la Tautología y Des-mockear la Prueba Golden de AST (`GAP-0.4-09`)
* **Origen:** `E-0.4-302`
* **Acción:** En `tests/integration/test_golden_parser.py`, eliminar la asignación `expected_fingerprint = current_fingerprint` y la intercepción por `patch.object`. Generar el AST real sobre `sample_3_pages.pdf` y compararlo estrictamente contra `sample_3_pages.fingerprint.json`.

#### REC-0.4.4-02 — Absorber el Mapeo V1 $\rightarrow$ V2 en el Parser Nativo
* **Origen:** `E-0.4-301`
* **Acción:** Refactorizar `parse_pdf()` y `FlatASTBuilder` para emitir la ontología canónica `ContentNodeType` V2 directamente, eliminando el *monkey-patch* (`custom_ast_node_factory`) en `test_real_paper.py`.

#### REC-0.4.4-03 — Construir una Prueba Walking Skeleton Sin Mocks Internos
* **Origen:** `E-0.4-309`
* **Acción:** Diseñar una prueba en `tests/integration/` que ejecute el pipeline completo sobre un PDF real de 1 página ($\text{PDF} \rightarrow \text{AST V2} \rightarrow \text{Chunker} \rightarrow \text{LLM Fake} \rightarrow \text{Assembler} \rightarrow \text{LaTeX}$), sin parchear `pipeline.execute()`.

#### REC-0.4.4-04 — Sincronizar la Nomenclatura de Pruebas
* **Origen:** `E-0.4-303`, `E-0.4-309`
* **Acción:** Renombrar archivos que usan prefijos "Real" o "E2E" pero que prueban contratos miqueados (ej. `test_real_parser_pipeline.py` $\rightarrow$ `test_pdf_adapter_contracts.py`).










"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""












# HITO_0.4.4_REGRESSION_ARCHITECTURE_AUDIT.md
## Test Architecture, Invariants, Mocks & Regression Barriers Forensic Audit — Reporte Consolidado Final

* **Estado:** FROZEN / CONGELADO (Cierre de Hito 0.4)
* **Fecha de Emisión:** 2026-07-27
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.4
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Auditoría analítica y forense estricta basada en la inspección del 100% de la suite de pruebas (`tests/integration/` y `tests/unit/`). Cero mutaciones en código productivo.

---

## 1. DICTAMEN EJECUTIVO: EL MITO DEL "PYTEST VERDE"

La suite de pruebas de Traductor no debe considerarse actualmente una superficie homogénea de certificación. Existe un núcleo sólido y brillante de pruebas de correctitud, invariantes y topología. Sin embargo, ese núcleo convive con un ecosistema de tests débiles, tautológicos, contractualmente obsoletos y pruebas que continúan certificando arquitecturas históricas[cite: 1].

**Veredicto:** `pytest passed` no constituye actualmente evidencia suficiente de integridad arquitectónica. El sistema padece de una superposición de generaciones arquitectónicas que contamina la fidelidad de la regresión.

---

## 2. HALLAZGOS CRÍTICOS: TAUTOLOGÍAS Y OBSOLESCENCIA

El análisis profundo del último bloque unitario, cruzado con las pruebas de integración, revela cuatro patrones de alto riesgo que invalidan silenciosamente las barreras de regresión:

### A. Tautología Pura (El test se mockea a sí mismo)
* **Origen:** `tests/unit/test_summary_builder.py`[cite: 1]
* **Evidencia:** Se ejecuta un `patch.object(SummaryBuilder, 'build', return_value=mock_summary)` para luego invocar `SummaryBuilder.build()`. 
* **Diagnóstico:** El test no ejecuta la implementación productiva. Prueba únicamente que un objeto mock configurado devuelve los atributos configurados. Su valor de regresión es **nulo**.

### B. Tautología Defensiva (Sobrevivencia vs Correctitud)
* **Orígenes:** `tests/integration/test_golden_parser.py` y `tests/test_pipeline_fidelity.py`[cite: 1]
* **Evidencia:** 
  * En el parser Golden: `expected_fingerprint = current_fingerprint`.
  * En Fidelity: `target_type = getattr(ContentNodeType, "COMPOSITE_BLOCK", node.node_type)` seguido de `assertEqual(node.node_type, target_type)`.
* **Diagnóstico:** El uso de `getattr` con un *fallback* hacia el valor actual, o la igualación directa del oráculo a la variable bajo prueba ($A == A$), permite que el test pase incluso si el contrato subyacente ha sido destruido o eliminado.

### C. Certificación de Arquitectura Obsoleta (Deuda Activa)
* **Origen:** `tests/unit/test_routing.py`[cite: 1]
* **Evidencia:** El test certifica el modelo histórico de enrutamiento basado en `ProviderStrategy` (ej. `GROQ_HEAVY`, `BYPASS`). Sin embargo, la arquitectura estabilizada de la Fase 16.4 define `TranslationRouter`, `NodeRouter` y `RouteChannel` (`TRANSLATE`, `PASSTHROUGH`, `OMIT`).
* **Diagnóstico:** Esto es severo. El test es evidencia viva de que la suite conserva y exige el cumplimiento de una arquitectura que ya fue reemplazada en el código productivo.

### D. Contratos de Frontera Desactualizados
* **Origen:** `tests/unit/test_prompt_builder.py`[cite: 1]
* **Evidencia:** La prueba instancia un `PromptBuilder` inyectando un `InferenceMeasurementService` directamente, lo cual no corresponde a la firma ni a la composición de dependencias de la arquitectura FinOps actual.

---

## 3. EL NÚCLEO SÓLIDO: GARANTÍAS REALES DEL SISTEMA

Pese a los hallazgos negativos, la suite alberga un baluarte de rigor técnico in-memory que sí representa el estándar SOTA deseado:

* **Zhang-Shasha TED (`test_zhang_shasha.py`):** Pruebas matemáticas impecables[cite: 1]. Valida isomorfismo, simetría, violaciones de orden post-orden y escalabilidad (150 nodos) sin el uso de mocks.
* **Score Policy (`test_score_policy.py`):** Inmutabilidad y cálculo determinista compuesto sin dependencias de I/O[cite: 1].
* **Structural Healing (`test_structural_healing.py`):** Cobertura exhaustiva de auto-cierre de llaves, protección de regiones *verbatim* y políticas de límite de autofix[cite: 1].
* **Topology Metrics (`test_structural_metric.py`):** Pruebas de sensibilidad al aplanamiento jerárquico y reordenamiento de nodos hermanos[cite: 1].
* **FSM y Resiliencia (`test_recovery_flow.py`, `test_cache_provider.py`):** Integración real contra bases de datos SQLite en disco, validando rescate de trabajos `STALLED` y mitigación de *Cache Stampede* bajo estrés de corrutinas asíncronas[cite: 1].

---

## 4. TAXONOMÍA EVOLUTIVA (LAS 3 GENERACIONES DE PRUEBAS)

El problema subyacente de la suite es la superposición histórica. Hemos identificado tres generaciones conviviendo bajo el mismo directorio:

1. **Generación A (Arquitectura Histórica):**
   * *Características:* Contratos antiguos, enrutamiento `ProviderStrategy`, DTOs deprecados.
   * *Ejemplos:* `test_routing.py`, `test_prompt_builder.py`.
2. **Generación B (Arquitectura de Transición):**
   * *Características:* Código defensivo, abuso de `Any`, uso de `getattr` con fallbacks, inyección de Mocks masivos para sobrevivir a refactores estructurales (Over-Mocking).
   * *Ejemplos:* `test_pipeline_fidelity.py`, `test_real_parser_pipeline.py`, "E2E" tests que parchean `pipeline.execute()`.
3. **Generación C (Arquitectura Estabilizada - SOTA):**
   * *Características:* AST V2, Topology, Zhang-Shasha, Invariantes, Snapshots deterministas, FSM real.
   * *Ejemplos:* `test_zhang_shasha.py`, `test_chunker_snapshot.py`, `test_structural_healing.py`.

---

## 5. CONCLUSIÓN ARQUITECTÓNICA Y DISPOSICIÓN FINAL

El **Hito 0.4.4** queda oficialmente cerrado con la siguiente disposición rectora para la inminente fase de saneamiento (Hito 0.5):

**"Un test no es evidencia de calidad porque pase; es evidencia únicamente si falla cuando se viola el contrato correcto y si su oráculo es estrictamente independiente de la implementación que pretende certificar."**

### Plan de Remediación (No Bloqueante para Cierre de Hito 0.4):
La suite debe someterse a una purga selectiva regida por este árbol de decisión:

1. **¿Existe todavía el contrato que el test pretende verificar?**
   * *NO:* ELIMINAR el test (Ej. `test_routing.py`).
   * *SÍ:* Avanzar al paso 2.
2. **¿El oráculo (expected) es independiente del resultado actual?**
   * *NO:* REESCRIBIR eliminando tautologías (Ej. `test_golden_parser.py`, `test_pipeline_fidelity.py`).
   * *SÍ:* Avanzar al paso 3.
3. **¿Prueba el comportamiento real del componente?**
   * *NO:* REDISEÑAR eliminando *monkey-patching* interno (Ej. `test_summary_builder.py`).
   * *SÍ:* CONSERVAR como parte del baseline canónico (Ej. `test_zhang_shasha.py`, `test_recovery_flow.py`).

---
**DICTAMEN FINAL FASE 0:** Toda la auditoría de descubrimiento ha concluido. El sistema, sus fronteras, topologías, contratos y deficiencias de prueba han sido mapeados con éxito. 
**Paso al Hito 0.5: Formal Architectural Disposition & Freeze Gate.**













"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""












# HITO_0.4.4_BENCHMARK_ARCHITECTURE_AUDIT.md
## Core Benchmark Framework, LLM Runners & Statistical Engine Forensic Audit — Reporte Consolidado Bloque A

* **Estado:** REJECTED FOR PHASE 17 MERGE / REQUIRES DECOUPLING & SANITIZATION (Sub-Hito 0.4.4-B)
* **Fecha de Emisión:** 2026-07-27
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.4 (Sub-hito 0.4.4-B: Bloque A)
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Auditoría analítica y forense sobre la totalidad del módulo `core/benchmark/` (sin incluir el subdirectorio `topology/`). Cero mutaciones en código productivo.

---

## 1. DICTAMEN EJECUTIVO: LA DUALIDAD ARQUITECTÓNICA DEL BLOQUE A

El escrutinio del módulo `core/benchmark/` revela una **esquizofrenia de diseño crítica**: el módulo alberga simultáneamente un **motor de evaluación estadística no paramétrica de grado científico impecable** y un **conjunto de ejecutores y jueces heredados que violan las fronteras de Capa Limpia (Hexagonal) y responden a un problema de dominio desactualizado**.

```text
[ ARQUITECTURA DEL BLOQUE A: CORE/BENCHMARK ]

┌─────────────────────────────────────────────────────────────────────────┐
│                          1. NÚCLEO SÓLIDO SOTA                          │
├─────────────────────────────────────────────────────────────────────────┤
│  • reporter.py      ──► Mann-Whitney U, KS-2samp, Cliff's Delta,       │
│                         Bootstrap CI 95%, Holm-Bonferroni (FWER).       │
│  • score_policy.py  ──► Ponderación inmutable, pesaje 1.0, Fail-Fast.   │
│  • ports.py         ──► Abstracciones puras (DIP) vía typing.Protocol.  │
│  • quality.py       ──► Validez sintáctica AST vía pylatexenc/markdown_it│
└─────────────────────────────────────────────────────────────────────────┘
                                     ▲
                                     │   DIVERGENCIA ARQUITECTÓNICA
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    2. CAPA HEREDADA Y DESTRUCTIVA                       │
├─────────────────────────────────────────────────────────────────────────┤
│  • runners/         ──► Invocan la app de traducción (AsyncDispatcher)  │
│                         para medir inferencia LLM en vez de Extracción  │
│                         PDF. Invierten dependencias (Core ──► Apps).    │
│  • semantic_judge.py──► SDK externo (AsyncGroq) incrustado en el Core.  │
│                         Sin versionado de juez ni taxonomía de errores. │
│  • judge_prompts.py ──► Exige Chain-of-Thought innecesario; rúbrica      │
│                         ordinal combinada con floats continuos.         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Veredicto:** **NO APROBADO EN SU ESTADO ACTUAL.** El módulo `core/benchmark/` no puede congelarse homogéneamente. Se debe preservar y aislar el motor estadístico/scoring, mientras que los ejecutores LLM (`runners/`) y el juez (`semantic_judge.py`) deben ser desacoplados y extraídos del núcleo de la Fase 17.

---

## 2. HALLAZGOS CRÍTICOS Y VIOLACIONES ARQUITECTÓNICAS (P0 / P1)

### GAP-0.4-10: Desalineación de Dominio con la Fase 17 (Extraction Engine Integration)
* **Origen:** `core/benchmark/runners/gemini_runner.py` y `groq_runner.py`
* **Análisis Forense:** 
  * El objetivo explícito de la Fase 17 es la **integración y comparación de motores de extracción física** (PyMuPDF vs. Docling vs. Marker vs. Nougat). La cadena de valor esperada es: $\text{PDF} \rightarrow \text{DocumentLayout} \rightarrow \text{AST V2} \rightarrow \text{Ground Truth} \rightarrow \text{Topology Metrics}$.
  * Sin embargo, `GeminiBenchmarkRunner` y `GroqBenchmarkRunner` instancian la infraestructura de inferencia y traducción de texto (`AsyncDispatcher`, `PromptBuilder`, `RateLimitedProvider`, `TranslationUnit`). 
  * Miden tokens consumidos ($TPM$), límites de tasa ($RPM$), costo en $USD$ y desbordamiento de contexto. **Miden la inferencia de traducción, no la fidelidad de extracción topológica del PDF.**

### GAP-0.4-11: Violación Inversa de la Arquitectura Hexagonal (`core` $\rightarrow$ `apps`)
* **Origen:** `core/benchmark/runners/gemini_runner.py`, `groq_runner.py` y `semantic_judge.py`
* **Análisis Forense:**
  * Los runners importan directamente desde la capa de aplicación e infraestructura:
    ```python
    from apps.llm_workers.adapters import GeminiProvider, GroqProvider
    from apps.llm_workers.rate_limiter import RateLimitedProvider
    from apps.llm_workers.dispatcher import AsyncDispatcher
    ```
  * Asimismo, `semantic_judge.py` incrusta el SDK de infraestructura directamente en el dominio:
    ```python
    from groq import AsyncGroq  # CONTAMINACIÓN DIRECTA DEL CORE
    ```
  * **Efecto:** Invierte la Regla de Dependencias de la Arquitectura Limpia. El núcleo de benchmarking depende de implementaciones concretas de la capa de aplicación y SDKs de terceros en lugar de depender únicamente de los puertos abstractos declarados en `ports.py`.

### GAP-0.4-12: Deficiencias Metodológicas en `semantic_judge.py` y `judge_prompts.py`
* **Origen:** `core/benchmark/judge_prompts.py` y `semantic_judge.py`
* **Análisis Forense:**
  1. **Acoplamiento Físico de Proveedor:** `SemanticJudge` es un envoltorio rígido sobre Groq + `llama-3.3-70b-versatile`, imposibilitando la sustitución por otros jueces (Gemini, OpenAI, modelos locales) sin modificar el `core/`.
  2. **Incoherencia en la Escala de Puntuación:** La rúbrica establece una escala ordinal discreta ($1.0, 2.0, 3.0, 4.0, 5.0$), pero los DTOs en `judge_models.py` declaran campos `float` abiertos. Esto permite puntuaciones ambiguas como $3.7$ que rompen la semántica de los niveles Q1 de la rúbrica.
  3. **Forzamiento Innecesario de Chain-of-Thought (CoT):** El prompt exige colocar `judge_reasoning` al principio del JSON para "forzar Chain-of-Thought". En benchmarking automatizado, esto incrementa la latencia y la variabilidad de tokens generados sin proveer un contrato de evidencia observable directa (`rationale` conciso).
  4. **Ausencia de Trazabilidad e Identidad de Juez:** El resultado devuelto (`ChunkEvaluationScore`) no registra la identidad del juez (`judge_provider`, `judge_model`, `prompt_version`, `rubric_version`, `source_sha256`, `target_sha256`). `temperature=0.0` no garantiza reproducibilidad científica si cambian las versiones del modelo remoto o el prompt.
  5. **Manejo de Reintentos Frágil:** Filtra errores por subcadenas (`"429" in error_msg.lower()`) e implementa un *backoff* exponencial sin *jitter* dentro de la lógica del evaluador, en lugar de delegar el reintento al adaptador de red.

### GAP-0.4-13: Métricas Falsas e Instrumentación Defectuosa en Runners
* **Origen:** `core/benchmark/runners/gemini_runner.py`
* **Análisis Forense:**
  1. **Telemetría de Memoria Distorsionada:** 
     ```python
     mem_info = process.memory_info()
     HardwareTelemetry(
         cpu_peak_percent=psutil.cpu_percent(interval=0.1),
         rss_peak_mb=round(mem_info.rss / (1024 * 1024), 2),
         rss_avg_mb=round(mem_info.rss / (1024 * 1024), 2),  # ERROR: peak == avg
         sampling_interval_ms=100
     )
     ```
     Toma una muestra instantánea en lugar de un muestreo continuo en un hilo dedicado, forzando que `rss_peak_mb` sea siempre exactamente igual a `rss_avg_mb`.
  2. **Denominación Mismatch en Compresión:**
     ```python
     compression_ratio_used = round(out_tokens / in_tokens, 4)
     ```
     La relación $\frac{\text{output\_tokens}}{\text{input\_tokens}}$ mide la tasa de expansión/generación, no de compresión. Además, si $\text{in\_tokens} == 0$, devuelve $1.0$, inventando un valor arbitrario.
  3. **Simulación Falsa de Warmup:** El método `warmup()` mide el tiempo de instanciación de objetos de Python en memoria (`time.monotonic()`), sin realizar ninguna llamada de red real para "calentar" las conexiones HTTP ni las cuotas de la API.
  4. **Inferencia Frágil de Rechazo Local:** Define `is_local_rejection = (not success) and (latency == 0.0)`. Inferir la etapa de un fallo a partir de la latencia cero asume que la telemetría siempre registra tiempo, en lugar de exigir un estado explícito de la falla (`stage = PRE_NETWORK | NETWORK | POST_NETWORK`).

---

## 3. EL NÚCLEO CIENTÍFICO RESCATABLE (COMPONENTES SOTA)

A pesar de los fallos en la capa de ejecución de inferencia, la infraestructura analítica de `core/benchmark/` es **SOTA y de calidad de publicación**:

1. **`core/benchmark/reporter.py` (`StatisticalComparator`):**
   * **Invariante:** Implementa pruebas de hipótesis no paramétricas bilaterales con Mann-Whitney U y Kolmogorov-Smirnov de 2 muestras.
   * **Invariante:** Mide el tamaño del efecto real mediante Cliff's Delta ($\text{cliffs\_d} = \frac{2U}{n_1 n_2} - 1$) clasificándolo en categorías estándar (`negligible`, `small`, `medium`, `large`).
   * **Invariante:** Genera intervalos de confianza al 95% para la mediana y percentil 95 mediante Bootstrap ($n=1000$).
   * **Invariante:** Aplica el ajuste paso a paso de Holm-Bonferroni sobre los $p$-valores para controlar la tasa de error por familia (FWER) en evaluaciones múltiples.

2. **`core/benchmark/score_policy.py` (`ScorePolicy`):**
   * **Invariante:** Garantiza que los pesos de las reglas sumen exactamente $1.0$ ($\pm 1e-5$).
   * **Invariante:** Aplica la dirección de optimización (`HIGHER_IS_BETTER` / `LOWER_IS_BETTER`) sobre valores estrictamente normalizados en $[0.0, 1.0]$, rechazando `NaN`, infinitos y valores fuera de rango via `InvalidMetricValueError`.
   * **Invariante:** Inmutabiliza las reglas mediante `MappingProxyType` y valida presencia atómica mediante *Fail-Fast* (`MissingMetricError`, `UnknownMetricRuleError`).

3. **`core/benchmark/quality.py` (`StructuralQualityEvaluator`):**
   * **Invariante:** Evalúa la validez de LaTeX mediante parseo real de AST usando `pylatexenc.latexwalker.LatexWalker`.
   * **Invariante:** Evalúa la integridad de tablas Markdown mediante el parser GFM `markdown_it.MarkdownIt`, verificando el balance exacto de tokens `table_open` y `table_close`.

---

## 4. MATRIZ DE AUDITORÍA FORENSE DEL BLOQUE A (`core/benchmark/`)

| Archivo / Artefacto | Propósito en el Sistema | Diagnóstico de Calidad | Severidad | Estado para Fase 17 |
| :--- | :--- | :--- | :---: | :--- |
| `models.py` | DTOs de telemetría y ejecución | **SOTA:** Inmutable, `slots=True`, `frozen=True`. | Ok | **CONSERVAR** |
| `ports.py` | Interfaces puras (DIP) | **SOTA:** Uso correcto de `@runtime_checkable` `Protocol`. | Ok | **CONSERVAR** |
| `orchestrator.py` | Driver de evaluación A/B y candidatos | **SOTA:** Valida SHA-256 de datasets y soporta polimorfismo. | Ok | **CONSERVAR** |
| `persistence.py` | Almacenamiento de reportes/vectores | **SOTA:** Desacoplado, exporta vectores crudos JSON y Markdown. | Ok | **CONSERVAR** |
| `quality.py` | Validadores AST LaTeX y GFM | **SOTA:** Uso de `pylatexenc` y `markdown_it`. Cero mocks. | Ok | **CONSERVAR** |
| `reporter.py` | Comparador Estadístico & Leaderboard | **CIENTÍFICO:** Mann-Whitney, KS, Cliff's Delta, Holm-Bonferroni. | Ok | **CONSERVAR (SOTA)** |
| `score_policy.py` | Reglas y pesos de puntuación | **EXCELENTE:** Inmutable, Fail-Fast, validación flotante IEEE 754. | Ok | **CONSERVAR** |
| `aggregation.py` | Techos y penalizaciones de score | **ACEPTABLE:** Lógica de penalización cuadrática por fidelidad. | Media | **REVISAR** |
| `types.py` | Enums y marcadores base | **DEBIL:** `ProviderKind` demasiado genérico; `BenchmarkArtifact` vacío. | Media | **REFACTORIZAR** |
| `judge_prompts.py` | Prompts para LLM-as-a-Judge | **DEFECTUOSO:** Exige CoT; rúbrica ordinal vs. floats. | Alta | **REDISCUTIR** |
| `semantic_judge.py` | Evaluador cualitativo vía Groq | **CRÍTICO:** Importa `AsyncGroq` en `core/`; sin versionado. | Crítica | **EXTRAER A ADAPTERS** |
| `gemini_runner.py` | Runner de inferencia Gemini | **CRÍTICO:** Mide traducción LLM, no extracción PDF. Viola Hexagonal. | Crítica | **DEPRECAR DE F17** |
| `groq_runner.py` | Runner de inferencia Groq | **CRÍTICO:** Mide traducción LLM, no extracción PDF. Viola Hexagonal. | Crítica | **DEPRECAR DE F17** |

---

## 5. HOJA DE RUTA Y RECOMENDACIONES ARQUITECTÓNICAS (HITO 0.5)

Para sanear el Bloque A y alinear la infraestructura de benchmarking con los objetivos de la Fase 17, se dictaminan las siguientes acciones no bloqueantes para la congelación del Hito 0.4:

1. **REC-0.4.4-05 — Segregar el Benchmark de Extracción del Benchmark de Inferencia:**
   * Mover `gemini_runner.py` y `groq_runner.py` fuera del camino crítico de la Fase 17. Crear ejecutores específicos para los extractores de PDFs (`PyMuPDFRunner`, `DoclingRunner`, `MarkerRunner`) que consuman `ExtractionProvider` y emitan `DocumentLayout` / `AST V2`.

2. **REC-0.4.4-06 — Erradicar la Inyección de SDKs Externos del Core (`semantic_judge.py`):**
   * Convertir `semantic_judge.py` en una interfaz pura `SemanticJudgePort` dentro de `core/benchmark/ports.py`. Trasladar la implementación concreta con `AsyncGroq` a `infra/adapters/benchmarks/groq_judge_adapter.py`.

3. **REC-0.4.4-07 — Reestructurar el Prompt y el Contrato del LLM-as-a-Judge:**
   * Sustituir la petición de Chain-of-Thought inicial por un campo `rationale` conciso. Reemplazar los floats abiertos por tipos discretos alineados con la rúbrica Q1 ($1.0, 2.0, 3.0, 4.0, 5.0$) e inyectar identificadores inmutables de trazabilidad (`judge_model`, `prompt_hash`, `dataset_sha256`) en el reporte final.

4. **REC-0.4.4-08 — Corregir la Telemetría de Hardware y Mapeo de Errores:**
   * Implementar un hilo/corrutina de monitoreo continuo en `psutil` para capturar el pico real de memoria RSS (`rss_peak_mb`) y el promedio real (`rss_avg_mb`). Renombrar `compression_ratio_used` a `expansion_ratio` y basar la detección de fallos locales en campos explícitos de etapa (`ExecutionStage`) y no en la latencia cero.

---

## 6. DECLARACIÓN DE CIERRE DEL BLOQUE A (Sub-hito 0.4.4-B)

El **Bloque A (Core Benchmark Framework)** del Sub-hito 0.4.4-B queda **AUDITADO Y REGISTRADO**. 

Sus componentes SOTA (`reporter.py`, `score_policy.py`, `quality.py`, `orchestrator.py`, `ports.py`) quedan aprobados para ser reutilizados en la evaluación topológica, mientras que sus componentes legacy (`runners/`, `semantic_judge.py`) quedan marcados para refactorización y desacoplamiento en el **Hito 0.5**.






"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""









# HITO_0.4.4_C1_GOLDEN_IDENTITY_TOPOLOGY_AUDIT.md
## Auditoría Forense de Infraestructura, Identidad Criptográfica y Motor de Topología — Reporte Consolidado Bloque C1

* **Estado:** CLOSED & FROZEN / CERRADO Y CONGELADO (Bloque C1)
* **Fecha de Emisión:** 2026-07-27
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.4 (Sub-hito 0.4.4-C: Bloque C1)
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Auditoría analítica y forense sobre la infraestructura de `core/benchmark/topology/`, `tools/evaluation/` y mecanismos de sellado de identidad. Cero mutaciones en código productivo.

---

## 1. DICTAMEN EJECUTIVO: ESTADO REAL DEL SUBSISTEMA DE EVALUACIÓN TOPOLÓGICA

El escrutinio del Bloque C1 confirma que **el subsistema de evaluación topológica y la cadena de generación de candidatos para la Fase 17 están completamente materializados, conectados y listos para uso experimental**.

```text
[ CIRCUITO Y PIPELINE CANÓNICO DE EVALUACIÓN TOPOLÓGICA (FASE 17) ]

  Corpus PDFs (tests/corpus/calibration_v1/pdf)
        │
        ├──► Extraction Providers (PyMuPDF, Docling)
        │         │
        │         ▼
        │    DocumentLayout ──► LayoutValidator (Fail-Fast)
        │         │
        │         ▼
        │    FlatASTBuilder ──► Candidate AST V2 JSONs
        │                            │
        └──► Sealed Ground Truth ─────┤ (Cryptographic SHA-256 Seal)
             (freeze_ground_truth)   │
                                     ▼
                        Topology Benchmark Engine
                        (core/benchmark/topology/)
                         ├── Alignment & Partitioning (Heading/Anchor)
                         ├── Zhang-Shasha Engine / PostorderIndex
                         ├── Entity & Equation Recall Evaluators
                         └── Normalized Tree Edit Distance (TED)
                                     │
                                     ▼
                        Leaderboard & Reports
                        (JsonReportFormatter / MarkdownReportFormatter)
```

**Veredicto:** **BLOQUE C1 CERRADO Y APROBADO COMO LÍNEA DE BASE DE INFRAESTRUCTURA.** No se requiere inventar nueva batería de pruebas ni reestructurar el motor topológico. La infraestructura existe, los contratos están desacoplados y la CLI unificada en `run_benchmark.py` es operativa.

---

## 2. HALLAZGOS Y EVIDENCIAS DE ARQUITECTURA (C1)

### A. Madurez de la Rama Topológica Nativa (`core/benchmark/topology/`)
El subsistema topológico trasciende la simple comparación de cadenas:
1. **Contratos e Interfaces Limpias (`ports.py`):** Definición estricta de puertos abstractos (`NodeCorrespondencePolicy`, `ContentSimilarityPolicy`, `EditCostPolicy`, `NodeMatchingPolicy`, `AnchorAlignmentStrategy`, `AnchorPartitionStrategy`, `TreeDistanceAlgorithm`, `TreeEditEngine`, `OverflowStrategy`, `NormalizationPolicy`).
2. **Evaluadores de Dominio:** Presencia de `TreeEditDistanceEvaluator` (programación dinámica sobre árbol post-orden) y `EntityRecallEvaluator` (recuperación de ecuaciones, tablas y títulos).
3. **Estructura de Datos Data-Oriented:** Implementación de `PostorderIndex` para representar árboles en arreglos columnares inmutables optimizados para memoria y velocidad.

### B. Verificación de la Suite de Pruebas Zhang-Shasha (`tests/unit/test_zhang_shasha.py`)
Se confirma la existencia de una suite de pruebas unitarias matemáticamente rigurosa para el motor de distancia de edición de árboles (*Zhang-Shasha TED*), cubriendo:
* Árboles vacíos, nodos individuales e identidad ($TED=0.0$).
* Inserción, borrado y sustitución atómica.
* Isomorfismo e independencia de IDs de nodos.
* Simetría ($TED(A, B) == TED(B, A)$).
* Violaciones a la invariante de orden post-orden (`IndexConsistencyError`).
* Bosques multi-raíz, árboles de gran profundidad y estructuras anchas.
* Pruebas de escalabilidad y robustez hasta 150 nodos.

### C. Herramientas CLI y Evolución del Entrypoint (`tools/evaluation/`)
1. **Entrypoint Unificado:** `run_benchmark.py` constituye la fachada CLI oficial que resuelve el `MetricRegistry`, ejecuta `TopologyBenchmarkService` y emite reportes en Markdown y JSON.
2. **Deprecaación Transparente:** `run_experimental_benchmark.py` emite `DeprecationWarning` y redirige al entrypoint unificado.
3. **Sellado Criptográfico:** `freeze_ground_truth.py` y `bootstrap_corpus.py` garantizan la inmutabilidad de los *Ground Truths* verificando hashes SHA-256 globales.
4. **Separación de Archivos Históricos:** La carpeta `tools/benchmark_archive/` contiene herramientas y scripts de experimentos pasados (Fase 7 a 15) que no contaminan el camino activo.

---

## 3. DEUDA TÉCNICA NO BLOQUEANTE IDENTIFICADA EN C1

Los siguientes hallazgos se registran como deuda técnica documentada que no impide el cierre del Bloque C1:

1. **Sustitución de Oráculo en Test de Regresión (`GAP-0.4-09`):**
   En `tests/integration/test_golden_parser.py`, la línea `expected_fingerprint = current_fingerprint` degrada el oráculo congelado en disco. El test ejecuta el parser pero no actúa como una barrera estricta de regresión. *(Prioridad: Reescritura en Hito 0.5)*.
2. **Duplicación Parcial en Generación de Candidatos:**
   Existe `tools/evaluation/generate_pymupdf_candidate.py` junto al generador general `tools/evaluation/generate_candidates.py --provider pymupdf`. *(Prioridad: Consolidación en Hito 0.5)*.
3. **Coexistencia Histórica de Benchmarks:**
   `core/benchmark/` contiene tanto la infraestructura histórica de inferencia LLM (Fase 16) como la topológica (Fase 17). Son contextos evolutivos que no bloquean el uso de la rama topológica.

---

## 4. MATRIZ DE ESTADO Y DISPOSICIÓN CONSOLIDADA (BLOQUE C1)

| Artefacto / Subsistema | Función en Fase 17 | Estado de Implementación | Calidad / Diagnóstico | Disposición Hito 0.5 |
| :--- | :--- | :---: | :--- | :--- |
| `topology/models.py` | DTOs e índices de topología | **COMPLETO** | **SOTA:** Dataclasses congeladas (`slots=True`). | **CONSERVAR** |
| `topology/ports.py` | Contratos abstractos (DIP) | **COMPLETO** | **SOTA:** Protocols `@runtime_checkable`. | **CONSERVAR** |
| `topology/strategies.py` | Orquestación de micro-jueces | **COMPLETO** | **SOTA:** Composición inmutable. | **CONSERVAR** |
| `test_zhang_shasha.py` | Certificación matemática TED | **COMPLETO** | **SOTA:** Casos de borde algebraicos. | **CONSERVAR** |
| `bootstrap_corpus.py` | Indexación de corpus PDF | **COMPLETO** | **EXCELENTE:** SHA-256 de archivos. | **CONSERVAR** |
| `freeze_ground_truth.py` | Sellado de Ground Truth | **COMPLETO** | **SOTA:** Inmutabilidad del oráculo. | **CONSERVAR** |
| `generate_candidates.py` | CLI de extracción candidato | **COMPLETO** | **EXCELENTE:** Ingesta y validación AST. | **CONSERVAR** |
| `run_benchmark.py` | CLI unificada de Benchmark | **COMPLETO** | **SOTA:** Salidas Markdown/JSON. | **CONSERVAR** |
| `generate_pymupdf_candidate`| Generador específico PyMuPDF | **DUPLICADO** | **REDICIONABLE:** Solapa con CLI general. | **CONSOLIDAR** |
| `test_golden_parser.py` | Regresión de parser en CI | **DEGRADADO** | **TAUTOLÓGICO (`GAP-0.4-09`).** | **REESCRIBIR** |

---

## 5. DECLARACIÓN DE CIERRE DEL BLOQUE C1

El **Bloque C1 (Golden / Identity & Topology Core)** del Sub-hito 0.4.4-C queda **OFICIALMENTE AUDITADO, REGISTRADO Y CERRADO (`CLOSED`)**.

Se certifica que el repositorio posee la infraestructura topológica y las herramientas CLI necesarias para abordar la evaluación empírica de extractores en la Fase 17.

---

### TRANSICIÓN AL BLOQUE C2 (Parser / Structural Regression)

Iniciamos formalmente la auditoría del **Bloque C2: Parser / Structural Regression**.

Quedo a la espera de los archivos de este sub-bloque para evaluar el corazón del AST, el pipeline del parser de producción y las validaciones de estructura:

1. 📌 `core/ast/*` (modelos, builder, parser, validator)
2. 📌 `core/validation/ast/*`
3. 📌 `tests/integration/test_real_paper.py`










"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""









# HITO_0.4.4_C2_PARSER_STRUCTURAL_REGRESSION_AUDIT.md
## Core AST, Parsing Pipeline, Structural Validation & Regression Testing — Reporte Consolidado Bloque C2

* **Estado:** AUDIT CLOSED / REMEDIATION BACKLOG OPEN (Bloque C2)
* **Fecha de Emisión:** 2026-07-28
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.4 (Sub-hito 0.4.4-C: Bloque C2)
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Auditoría analítica y forense estricta sobre la totalidad del subsistema AST, extracción, enrutamiento, segmentación y validación pre-LLM (`core/ast/*`, `core/validation/ast/*`, `tests/integration/test_golden_parser.py`, `tests/integration/test_real_parser_pipeline.py`, `tests/integration/test_real_paper.py`, `tests/unit/test_layout_validator.py`). Cero mutaciones en código productivo.

---

## 1. PROPÓSITO Y ALCANCE

El **Sub-hito 0.4.4 (Bloque C2)** audita la integridad estructural, el cumplimiento de fronteras de arquitectura limpia, la coherencia de la máquina de estados de segmentación y la validez real de las barreras de regresión del parser. 

El objetivo central es destapar la deuda técnica acumulada, identificar falsas garantías de pruebas automatizadas y trazar la hoja de ruta de remediación para que la **Fase 17 (Extraction Engine Integration)** y la **Fase 17_BIS (Canonical Scientific Baseline)** operen sobre una canalización (*pipeline*) canónica, determinista y sin duplicaciones de código heredado.

---

## 2. REGISTRO DE EVIDENCIA FORENSE (E-0.4-321 a E-0.4-332)

### Evidencia E-0.4-321: Monolito de Ingesta Legacy y Acoplamiento Físico
* **Archivo Fuente:** `core/ast/parser.py`
* **Análisis Forense:** Se confirma que `parse_pdf()` es un artefacto monolítico de la Fase 11/12 que viola la arquitectura V2:
  * Hardcodea rutas físicas de Windows: `TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"`, destruyendo la portabilidad en Linux/Docker.
  * Inyecta un *bypass* forzado en la línea 104: `pdf_type, empty_pages = "OCR", []`, anulando por completo la clasificación dinámica del enrutador.
  * Bypassea la capa `DocumentLayout`, convirtiendo el PDF directamente en Markdown crudo y perdiendo para siempre la geometría física (`BoundingBox`), la lectura por columnas y el linaje espacial de las páginas.
  * Construye objetos `ASTNode` mediante *regular expressions* sobre cadenas de texto, canibalizando las responsabilidades del `FlatASTBuilder`.

---

### Evidencia E-0.4-322: Tautología en Pruebas Golden Parser (`GAP-0.4-09`)
* **Archivo Fuente:** `tests/integration/test_golden_parser.py`
* **Análisis Forense:** El test simula la verificación contra una huella congelada (`sample_3_pages.fingerprint.json`), pero invalida el oráculo mediante la asignación explícita `expected_fingerprint = current_fingerprint`. 
* **Resultado:** Las aserciones comparan `current_fingerprint` contra sí mismo ($A == A$). Además, miquea el método de extracción mediante `patch.object(self.adapter, 'parse', return_value=mock_nodes)` y fabrica una fixture inexistente escribiendo un texto plano (`%PDF-1.4 SOTA Dummy`). La prueba no detecta regresiones ni ejecuta el parser real.

---

### Evidencia E-0.4-323: Ilusión de Aislamiento en Test de Pipeline Real
* **Archivo Fuente:** `tests/integration/test_real_parser_pipeline.py`
* **Análisis Forense:** Bajo la clase `TestRealParserIsolation`, el test aplica un parche total sobre el adaptador: `with patch.object(self.adapter, 'parse', return_value=mock_nodes)`.
* **Resultado:** La prueba no analiza binarios PDF, no ejecuta PyMuPDF ni realiza OCR. Valida únicamente que una lista de nodos mock inyectados en memoria contenga atributos `node_id` no nulos. Actúa como un *contract test* de DTO, pero su nomenclatura sobre-promete una integración física inexistente.

---

### Evidencia E-0.4-324: Monkey-Patch de Compatibilidad V1 $\rightarrow$ V2 y Fixture Falsa
* **Archivo Fuente:** `tests/integration/test_real_paper.py`
* **Análisis Forense:** Es el único test que ejecuta la extracción física real llamando a `parse_pdf()`. Sin embargo:
  * Si el archivo PDF de prueba no existe, lo crea escribiendo una cadena textual corta, lo que provocaría un colapso en el motor C de PyMuPDF en un entorno limpio.
  * Inyecta un *monkey-patch* interceptando el constructor de nodos (`with patch("core.ast.parser.ASTNode", side_effect=custom_ast_node_factory)`). Este parche traduce la taxonomía Legacy V1 (`"EQUATION"`, `"TABLE"`) producida por el parser antiguo hacia la ontología V2 (`DISPLAY_EQUATION`, `TABLE_SIMPLE`) para evitar que `ASTValidator` arroje una excepción.

---

### Evidencia E-0.4-325: Duplicación de Segmentación (FSM Legacy vs. Segmenter V2)
* **Archivos Fuente:** `core/ast/segmenter.py` vs. `core/segmenter/*`
* **Análisis Forense:** Coexisten dos motores de segmentación paralelos en el repositorio:
  * `core/ast/segmenter.py` (`MarkdownSegmenter`): FSM legacy que opera sobre texto plano (`raw text -> List[str]`). Posee defectos críticos: el mecanismo Anti-Lock (TTL) emite bloques corruptos dándolos por válidos en lugar de aplicar *Fail-Fast*; no detecta estados abiertos al alcanzar el final de archivo (EOF); y no soporta anidamiento de entornos (ej. una ecuación dentro de una figura).
  * `core/segmenter/*` (Segmenter V2): Arquitectura congelada en Fase 16.3 que opera sobre el objeto inmutable `ASTNode` mediante `SegmentContext`, `BoundaryPolicy`, `SegmentDispatcher` y `ASTSequenceNormalizer`.

---

### Evidencia E-0.4-326: Violación de Arquitectura Hexagonal en Enrutador de Ingesta
* **Archivo Fuente:** `core/ast/router.py`
* **Análisis Forense:** `PDFRouter` reside dentro del dominio (`core/ast/`), pero importa directamente la librería de infraestructura `fitz` (PyMuPDF).
* **Defectos Detectados:**
  * Rompe la regla de independencia de tecnología de la Arquitectura Hexagonal.
  * Su arreglo `empty_pages` en realidad contabiliza páginas con menos de 300 caracteres, clasificando erróneamente portadas, tablas o páginas con una sola ecuación como "vacías".
  * El umbral de `300` caracteres es una constante mágica no contractualizada.
  * La apertura del documento `doc = fitz.open()` no está envuelta en un *context manager* (`with`), arriesgando fugas de descriptores de archivo ante excepciones.

---

### Evidencia E-0.4-327: Falsificación de Métricas de Observabilidad y APIs Muertas
* **Archivo Fuente:** `core/ast/validator.py`
* **Análisis Forense:**
  * `ASTHealthReport.semantic_coverage` calcula la cobertura dividiendo los nodos semánticos reconocidos sobre un total que *excluye* los nodos clasificados como `others`. Si un documento produce 10 párrafos y 90 nodos no reconocidos, la métrica reporta $10 / 10 = 100\%$ de cobertura semántica, engañando a los dashboards.
  * `ASTValidator.validate()` acepta los parámetros `unknown_count_floor` y `max_unknown_ratio`, pero ninguno de los dos se utiliza en el cuerpo de la función (APIs muertas).
  * Imprime `structural_coverage = 0.0%` como un valor numérico real en lugar de reportar `NOT_IMPLEMENTED`.
  * La validación TeX solo comprueba la existencia de cualquier apertura y cualquier cierre mediante expresiones regulares, sin validar paridad, orden ni balance jerárquico.

---

### Evidencia E-0.4-328: Mutabilidad Silenciosa en Matriz de Estrategias
* **Archivo Fuente:** `core/ast/strategy.py`
* **Análisis Forense:** `_STRATEGY_MAP` está anotado como `Final[Dict[ContentNodeType, TranslationStrategy]]`. Aunque `Final` impide la reasignación de la variable, el diccionario nativo subyacente sigue siendo mutable en tiempo de ejecución (`_STRATEGY_MAP.clear()`), violando los principios de inmutabilidad del dominio.

---

### Evidencia E-0.4-329: Motor Polimórfico de Validación AST V2 (SOTA)
* **Archivos Fuente:** `core/validation/ast/*` (`engine.py`, `extractors.py`, `factory.py`, `models.py`, `protocols.py`)
* **Análisis Forense:** Implementación de arquitectura limpia impecable.
  * `PolymorphicValidationEngine` utiliza un generador perezoso (`yield from validator.validate(node)`) que procesa el flujo en memoria $O(1)$ con consumo mínimo de RAM.
  * `StronglyTypedTextExtractor` realiza *pattern matching* sobre tipos de payload reales del dominio sin recurrir a reflexión ni Pydantic `model_dump()`.
  * `ValidationResult` y `ValidationSeverity` (`INFO`, `SOFT_FAIL`, `HARD_FAIL`) están aislados e inmutabilizados con `@dataclass(slots=True, frozen=True)`.

---

### Evidencia E-0.4-330: Normalización Trans-Página y Sutura Sintáctica (SOTA)
* **Archivo Fuente:** `core/ast/cross_page.py`
* **Análisis Forense:** Excelente motor de preservación léxica. `AbbreviationPolicy` verifica en $O(1)$ si un punto corresponde a una abreviatura científica (`et al.`, `i.e.`), evitando fusiones erróneas. `HyphenResolver` protege términos compuestos (ej. *T-cell*) durante la de-hyphenation trans-página, y `MetadataMerger` mantiene la trazabilidad conservando el nivel de confianza del segmento más degradado por el OCR.

---

### Evidencia E-0.4-331: Inmutabilidad y Factoría OCP de Payloads (SOTA)
* **Archivos Fuente:** `core/ast/builder.py`, `core/ast/models.py`, `core/ast/enums.py`
* **Análisis Forense:** 
  * `FlatASTBuilder` calcula la profundidad de anidamiento (`heading_stack`) en tiempo lineal $O(n)$ sin requerir árboles multidimensionales profundos.
  * `PayloadRegistry` mapea tipos de nodo a factorías mediante un diccionario estático, garantizando cumplimiento total del principio *Open/Closed (OCP)*.
  * `ASTNode` discrimina tipos de payload en Pydantic v2 de forma estricta mediante `@model_validator(mode="before")`.

---

### Evidencia E-0.4-332: Resiliencia de Invariantes Geométricas de Layout (SOTA)
* **Archivo Fuente:** `tests/unit/test_layout_validator.py`
* **Análisis Forense:** Suite de pruebas unitarias pura y robusta. Utiliza `model_construct()` para inyectar deliberadamente instancias de `BoundingBox` y `LayoutPage` corruptas o fuera de rango, certificando que `DocumentLayoutValidator` actúe como una barrera defensiva de dominio eficiente cuando la validación de Pydantic es omitida.

---

## 3. ANÁLISIS DE IMPACTO Y ARQUITECTURA DE DOMINIO

### 3.1 La Fractura del Pipeline: Visión Teórica vs. Ejecución Real

El análisis forense evidencia que el sistema sufre de una desconexión total entre su diseño canónico y su ejecución física:

```text
[ PIPELINE TEÓRICO CANÓNICO (FASE 17) ]
PDF ──► ExtractionProvider ──► DocumentLayout ──► DocumentLayoutValidator ──► FlatASTBuilder ──► AST V2 (Geometría + Texto)

[ PIPELINE REAL EN TIEMPO DE EJECUCIÓN (LEGACY) ]
PDF ──► core/ast/parser.py (Tesseract Win32 / PyMuPDF4LLM) ──► Raw Markdown ──► MarkdownSegmenter (Regex) ──► ASTNode (Sin Geometría)
```

### 3.2 Impacto sobre la Fase 17
Mientras `core/ast/parser.py` continúe destruyendo el PDF para convertirlo en texto plano antes de construir los nodos, se pierde toda la información geométrica (`BoundingBox`, coordenadas de columna, índice de página). Las abstracciones de `DocumentLayout` quedan huérfanas en la ingesta real, impidiendo la comparación de parsers en la Fase 17.

---

## 4. TAXONOMÍA Y MATRIZ DE AUDITORÍA FORENSE DE COMPONENTES Y TESTS

```text
[ CLASIFICACIÓN DE COMPONENTES DEL BLOQUE C2 ]

1. ARQUITECTURA ESTABILIZADA SOTA (CONSERVAR):
   ├── core/validation/ast/* (PolymorphicValidationEngine, Lazy Streaming, Severities)
   ├── core/ast/builder.py (FlatASTBuilder, PayloadRegistry, O(n) Topology)
   ├── core/ast/cross_page.py (CrossPageNormalizer, AbbreviationPolicy, HyphenResolver)
   ├── core/ast/models.py (ASTNode V2, Payloads Inmutables)
   ├── core/ast/hashing.py (TokenBudgetChunker, ContextAwareSemanticGrouper)
   └── tests/unit/test_layout_validator.py (Pruebas unitarias de invariantes físicas)

2. DEUDA ARQUITECTÓNICA Y RECONCILIACIÓN (REFACTORIZAR):
   ├── core/ast/router.py (Acoplamiento de fitz en core/ -> Migrar a infra/adapters)
   ├── core/ast/strategy.py (Mutabilidad en _STRATEGY_MAP -> Usar MappingProxyType)
   └── core/ast/validator.py (Métricas engañosas y APIs muertas -> Reemplazar por validation/ast)

3. ARTEFACTOS OBSOLETOS / LEGACY (RETIRAR):
   ├── core/ast/parser.py (Monolito de ingesta directa de Markdown/OCR)
   └── core/ast/segmenter.py (MarkdownSegmenter FSM sobre texto plano)

4. TESTS TAUTOLÓGICOS / DEFECTUOSOS (REESCRIBIR SIN MOCKS):
   ├── tests/integration/test_golden_parser.py (Tautología A == A; mock total de parse)
   ├── tests/integration/test_real_parser_pipeline.py (Falso aislamiento; mock total)
   └── tests/integration/test_real_paper.py (Monkey-patch de compatibilidad V1->V2; PDF falso)
```

| Componente / Archivo | Categoría | Dependencias Externas | Riesgo de Regresión | Disposición Hito 0.5 |
| :--- | :--- | :---: | :---: | :--- |
| `core/ast/builder.py` | Core Domain | **CERO** | Bajo | **CONSERVAR** |
| `core/ast/cross_page.py` | Core Domain | **CERO** | Bajo | **CONSERVAR** |
| `core/ast/enums.py` | Core Domain | **CERO** | Bajo | **CONSERVAR** |
| `core/ast/grouper.py` | Core Domain | **CERO** | Bajo | **CONSERVAR** |
| `core/ast/hashing.py` | Core Domain | Standard Lib | Bajo | **CONSERVAR** |
| `core/ast/models.py` | Core Domain | Pydantic v2 | Bajo | **CONSERVAR** |
| `core/ast/registry.py` | Core Domain | System FS | Medio | **LIMPIAR** (Quitar fallback a `tests/`) |
| `core/ast/router.py` | Ingesta | `fitz` (PyMuPDF) | **Alto** | **MIGRAR A INFRA** |
| `core/ast/segmenter.py` | Legacy FSM | **CERO** | **P0 (Crítico)** | **DEPRECAR / ELIMINAR** |
| `core/ast/strategy.py` | Routing Map | **CERO** | Medio | **INMUTABILIZAR** (`MappingProxyType`) |
| `core/ast/validator.py` | Observabilidad | **CERO** | **Alto** | **DEPRECAR** (Usar `validation/ast/`) |
| `core/validation/ast/*` | Core Validation | **CERO** | **Excelente** | **PROMOVER COMO CANÓNICO** |
| `test_golden_parser.py` | Integration Test | Mocks / Stubs | **P0 (Tautológico)** | **REESCRIBIR SOBERANO** |
| `test_real_parser_pipeline.py` | Integration Test | Mocks / Stubs | **P0 (Falso E2E)** | **RECONVERTIR A CONTRACT TEST** |
| `test_real_paper.py` | Integration Test | PyMuPDF real | **P1 (Frágil)** | **SANEATE** (Eliminar monkey-patch) |
| `test_layout_validator.py` | Unit Test | **CERO** | **Excelente** | **CONSERVAR Y EXPANDIR** |

---

## 5. REGLAS NORMATIVAS Y BACKLOG DE REMEDIACIÓN FUTURA (C2-R01 a C2-R11)

Queda prohibida la modificación de código durante la Fase 0. Las siguientes reglas constituyen el backlog técnico obligatorio de remediación para el **Hito 0.5** y la **Fase 17**:

* **C2-R01 (Prohibición de Evolución Legacy):** Queda estrictamente prohibido reactivar, añadir expresiones regulares o expandir el FSM de `core/ast/segmenter.py`. La segmentación del sistema debe realizarse exclusivamente a través de la arquitectura `core/segmenter/*` sobre objetos `ASTNode`.
* **C2-R02 (Aislamiento Hexagonal del Router):** Extirpar la importación de `fitz` de `core/ast/router.py`. La lógica de clasificación física debe migrar a `infra/adapters/document_metadata.py`. Renombrar el campo `empty_pages` a `low_text_pages` y formalizar el umbral de 300 caracteres como una política parametrizada.
* **C2-R03 (Retiro Programado del Parser Monolítico):** Programar la deprecación de `core/ast/parser.py`. La ingesta debe reencauzarse a través de proveedores que retornen `DocumentLayout` hacia `FlatASTBuilder`.
* **C2-R04 (Inmutabilidad Real en Estrategias):** Reemplazar `Final[Dict]` en `core/ast/strategy.py` por `MappingProxyType` para evitar mutaciones en tiempo de ejecución.
* **C2-R05 (Saneamiento de APIs Muertas):** Eliminar los parámetros inactivos `unknown_count_floor` y `max_unknown_ratio` de `ASTValidator.validate()`.
* **C2-R06 (Corrección de Fórmula de Cobertura Semántica):** Corregir el cálculo de `ASTHealthReport.semantic_coverage` incluyendo el contador `others` en el denominador para evitar falsos reportes de $100\%$. Eliminar la métrica falsa `structural_coverage = 0.0`.
* **C2-R07 (Clarificación del Motor de Validación):** Establecer explícitamente que `PolymorphicValidationEngine` opera como un componente de observación y detección (`Iterator[ValidationResult]`), delegando las decisiones de interrupción o penalización (*enforcement*) a los servicios de aplicación.
* **C2-R08 (Unificación de Proyección Textual):** Consolidar la extracción de texto en los validadores en torno a la propiedad facade `ASTNode.text_content`, evitando la coexistencia con extractores paralelos desalineados.
* **C2-R09 (Restauración de la Barrera Golden - P0):** Reescribir `test_golden_parser.py`. Eliminar la reasignación `expected_fingerprint = current_fingerprint` y el parche `patch.object`. La prueba debe procesar una fixture PDF real y comparar el AST resultante contra el archivo oráculo congelado en disco.
* **C2-R10 (Saneamiento del Test de Pipeline Real - P0):** Reconstruir `test_real_parser_pipeline.py` eliminando el parche sobre `adapter.parse()`. La prueba debe ejecutar la ingesta física real sobre el sistema de archivos. Si la fixture no existe, el test debe fallar o saltarse explícitamente (`skipTest`), prohibiendo la generación de PDFs falsos en texto plano.
* **C2-R11 (Creación de la Suite de Validación AST V2):** Diseñar e implementar una suite de pruebas unitarias dedicada en `tests/unit/validation/ast/` para certificar el funcionamiento de `PolymorphicValidationEngine`, `StronglyTypedTextExtractor` y los validadores estructurales sin depender de parches de integración.

---

## 6. ARQUITECTURA OBJETIVO DE LA FASE 17

El modelo de componentes que gobernará la reestructuración del Hito 0.5 queda fijado en la siguiente canalización unificada:

```text
                                         ┌─────────────────────┐
                                         │       PDF           │
                                         └──────────┬──────────┘
                                                    │
                                                    ▼
                                         ┌─────────────────────┐
                                         │ ExtractionProvider  │
                                         │     (PORT)          │
                                         └──────────┬──────────┘
                                                    │
                                     infraestructura│
                                                    ▼
                                         ┌─────────────────────┐
                                         │   PDF Adapter(s)    │
                                         │ PyMuPDF / Docling / │
                                         │ Marker / Nougat...  │
                                         └──────────┬──────────┘
                                                    │
                                                    ▼
                                         ┌─────────────────────┐
                                         │   DocumentLayout    │
                                         └──────────┬──────────┘
                                                    │
                                                    ▼
                                         ┌─────────────────────┐
                                         │ DocumentLayout      │
                                         │ Validator           │
                                         └──────────┬──────────┘
                                                    │
                                                    ▼
                                         ┌─────────────────────┐
                                         │   FlatASTBuilder    │
                                         └──────────┬──────────┘
                                                    │
                                                    ▼
                                         ┌─────────────────────┐
                                         │       AST V2        │
                                         │   INMUTABLE         │
                                         └──────────┬──────────┘
                                                    │
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
                 ▼                  ▼                  ▼
          Segmenter V2        Strategy Router     AST Validation
          core/segmenter     TRANSLATE/PASS       validation/ast
                 │                  │                  │
                 └──────────────────┼──────────────────┘
                                    ▼
                            Benchmark / Pipeline
```

---

## 7. EVALUACIÓN DE CONFIABILIDAD Y DECLARACIÓN DE CIERRE

### 7.1 DIAGNÓSTICO DE ALCANCE Y CONFIABILIDAD REAL
1. **Modelos de Dominio y Validación Polimórfica:** **100% SEGURO Y CONFIABLE.**
   `core/ast/models.py`, `core/ast/builder.py`, `core/ast/cross_page.py` y `core/validation/ast/*` constituyen una base de código excelente, fuertemente tipada e inmutable.
2. **Segmentación y Enrutamiento Legacy:** **INCIERTO / CORRUPTO.**
   `core/ast/segmenter.py` y `core/ast/router.py` introducen acoplamientos de infraestructura y comportamientos de máquina de estados que enmascaran errores de extracción.
3. **Barreras de Regresión en CI:** **INEXISTENTE / TAUTOLÓGICO (`GAP-0.4-09`).**
   Debido a los parches masivos y a la reasignación del oráculo en `test_golden_parser.py`, el CI actual es incapaz de detectar regresiones en la extracción de párrafos, tablas o ecuaciones.

---

### 7.2 DECISIÓN FINAL DEL SUB-HITO 0.4.4-C2

The audit for **Block C2 (Parser / Structural Regression)** is hereby declared **CLOSED**.

```text
====================================================================================
                  ESTADO DE AUDITORÍA: SUB-HITO 0.4.4-C2
====================================================================================
  Audit Status             | CLOSED (Auditoría Finalizada)
  Code Remediation         | DEFERRED (Diferido a Hito 0.5)
  Production Certification | NOT GRANTED (No Aprobado para Freeze en C2)
  Remediation Backlog      | OPEN (Reglas C2-R01 a C2-R11 Registradas)
====================================================================================
```

**Bitácora de Gobernanza:**
> *"Se da por concluida la auditoría del Bloque C2. Se identificaron defectos críticos en la suite de pruebas de integración (Golden Test tautológico y tests de parser que miquean la función evaluada), la convivencia de un segmentador legacy incompatible con la V2 y la falsificación de métricas de cobertura semántica. No se realizaron cambios en código durante C2. Los hallazgos se trasladan al Hito 0.5 como Backlog de Remediación Obligatorio, priorizando la restitución de la validez experimental de las pruebas antes de proceder al congelamiento de la línea de base."*











"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""










# HITO_0.4.4_C3_LAYOUT_REGRESSION_AUDIT.md
## Core Layout Engine, Document Profiling, Spatial Invariants & Structural Regression — Reporte Consolidado Bloque C3

* **Estado:** AUDIT CLOSED / REMEDIATION BACKLOG OPEN (Bloque C3)
* **Fecha de Emisión:** 2026-07-28
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.4 (Sub-hito 0.4.4-C: Bloque C3)
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Auditoría analítica y forense estricta sobre la totalidad de la capa de análisis bidimensional, inferencia de perfil documental, validador de maquetación y pruebas de regresión asociadas (`core/layout/*`, `core/document_profile/*`, `tests/unit/test_layout_validator.py`, `tests/integration/test_golden_parser.py`, `tests/integration/test_real_parser_pipeline.py`). Cero mutaciones en código productivo. Disposición diferida al Hito 0.5.

---

## 1. RESUMEN EJECUTIVO Y VEREDICTO ARQUITECTÓNICO

El Bloque C3 queda **AUDITADO Y REGISTRADO**, pero **NO se considera una capa de regresión estructural confiable ni aprobada para producción.**

La auditoría ha revelado que, si bien el código posee una base arquitectónica sofisticada (DTOs explícitos, abstracciones vía `Protocol`, etapas de pipeline aisladas, normalización geométrica, ordenamiento de lectura por barrido y grafos DAG), **existen fallas críticas de infraestructura, contratos engañosos y falsas garantías de seguridad en cuatro dimensiones principales**:

1. **La regresión Golden actual es falsa o tautológica:** Las pruebas de regresión principales no comparan contra un oráculo inmutable; se comparan contra sí mismas o mockean el objeto bajo prueba.
2. **El contrato runtime de `core/layout` no está garantizado:** Las fronteras aceptan tipos laxos (`dict[str, Any]`), hardcodean decisiones de perfil y emiten telemetría de éxito ante excepciones no capturadas.
3. **Divergencias taxonómicas y semánticas:** Coexisten tres niveles semánticos desalineados (`ContentNodeType`, `LayoutBlockType`, `str`), y la identidad por contenido se corrompe durante las fusiones espaciales.
4. **Garantías algorítmicas sobreprometidas:** Varios componentes afirman poseer propiedades de grado SOTA (inmutabilidad profunda, ordenamientos $O(n \log n)$, validación DAG) que la implementación en código no sostiene con rigor.

> **Principio de Cierre C3:** La prioridad futura no es optimizar los algoritmos de layout, sino convertir la regresión estructural en una **barrera científica real** mediante el blindaje del Golden Corpus y el benchmark con evidencia empírica.

---

## 2. MATRIZ DE CLASIFICACIÓN Y EVALUACIÓN GLOBAL

| Área / Archivo | Estado ArquITECTÓNICO | Severidad | Diagnóstico Forense |
| :--- | :--- | :---: | :--- |
| `document_profile/extractors.py` | Aceptable | **P2** | Abstracción limpia pero incompleta en la taxonomía de payloads. |
| `document_profile/models.py` | Razonable | **P1 / P2** | Falsa inmutabilidad profunda; `UNKNOWN` sobrecarga múltiples causas. |
| `document_profile/ports.py` | Dirección Hexagonal | **P2** | Puertos puros, requiere incluir versión y linaje en el `ProfileStore`. |
| `document_profile/profiler.py` | Separación Correcta | **P1** | Contrato de muestreo no garantiza representatividad de layout. |
| `document_profile/scoring.py` | Riesgo Métrico | **P1** | `winner()` puede emitir confianzas negativas y no calibra probabilidades. |
| `layout/base.py` | Infraestructura Útil | **P1** | Telemetría emite `SUCCESS` si ocurren excepciones fuera de `DomainException`. |
| `layout/builder.py` | Frontera Débil | **P0 / P1** | Inicia pipeline con `dict[str, Any]`; hardcodea idioma e ignora el Profiler. |
| `layout/classifier.py` | Heurística Útil | **P1** | Usa `str` como tipo; sobrepromete complejidad $O(1)$; math rompe código. |
| `layout/detector.py` | Heurística Espacial | **P1** | Asume coordenadas normalizadas sin contrato; etiqueta Sturges falsa. |
| `layout/identity.py` | Determinismo Local | **P1** | Semilla acoplada al `provider_name`, inutilizable como ID canónico. |
| `layout/merger.py` | Riesgo de Corrupción | **P0 / P1** | **CRÍTICO:** Cambia `content`/`bbox` pero conserva el `block_id` hash previo. |
| `layout/models.py` | Incompleto | **P1** | `frozen=True` con listas/dicts internos permite mutabilidad in-place. |
| `layout/normalizer.py` | Corrección Silenciosa | **P1** | `_scale_and_clamp` enmascara errores de extractor sin dejar diagnóstico. |
| `layout/reading_order.py` | Algoritmo Complejo | **P0 / P1** | Sweep-Line cae a $O(n^2)$; `_validate_dag_integrity` solo borra self-loops. |
| `layout/validator.py` | Barrera Inicial | **P1** | Insuficiente como auditor integral; arroja `AttributeError` en corruptos. |
| `test_golden_parser.py` | Falsa Regresión | **P0 (Crítico)** | **TAUTOLÓGICO:** Reasigna `expected_fingerprint = current_fingerprint`. |
| `test_real_parser_pipeline.py` | Falso E2E | **P0 (Crítico)** | Mockea `adapter.parse()` por completo y usa un PDF ficticio no válido. |
| `test_layout_validator.py` | Base Válida | **P2** | Pruebas unitarias de DTO sólidas pero con cobertura incompleta. |

---

## 3. REGISTRO DETALLADO DE HALLAZGOS FORENSES (C3-001 A C3-036)

### 3.1 Barreras de Regresión Falsas y Testing Tautológico

* **C3-001 — Golden Test Tautológico (`tests/integration/test_golden_parser.py`) [P0]:**
  El test carga el oráculo congelado `expected_fingerprint = json.load(f)`, pero inmediatamente ejecuta `expected_fingerprint = current_fingerprint`. La aserción se transforma en `current_fingerprint == current_fingerprint` ($A == A$). El test siempre pasa aunque el parser pierda ecuaciones, tablas o destruya la topología.
* **C3-002 — Falso Parser Real (`tests/integration/test_real_parser_pipeline.py`) [P0]:**
  El test se autodenomina "Real Parser Isolation", pero ejecuta `with patch.object(self.adapter, 'parse', return_value=mock_nodes)`. Jamás analiza un PDF, no ejecuta PyMuPDF ni OCR. Además, crea una fixture mediante `f.write("%PDF-1.4 SOTA Dummy")`, que no es un PDF binario válido.
* **C3-034 — Ausencia de Cobertura en `document_profile` [P2]:**
  No existen pruebas unitarias para `HeuristicLayoutDetector`, `HeuristicTypeDetector`, `ClassificationScores` ni `HeuristicDocumentProfiler`.
* **C3-035 — Fortalezas y Brechas en `test_layout_validator.py` [P2]:**
  Es el test más sano del bloque (valida páginas vacías, números de página duplicados, monotonicidad y BoundingBoxes inválidos), pero le falta auditar coherencia de `total_pages`, geometrías fuera de margen $[0, 1]$ y consistencia de `block_id`.
* **C3-036 — Cero Pruebas Unitarias Algorítmicas de Layout [P1]:**
  Ninguna etapa del pipeline ($2\text{D}$ Normalizer, Classifier, Detector, Merger, Reading Order) posee una batería de pruebas unitarias aisladas.

### 3.2 Pipeline, Contratos y Telemetría de Layout

* **C3-003 — Rompimiento de Contrato Inicial en `DocumentLayoutBuilder` (`builder.py`) [P1]:**
  Las etapas declaran consumir `LayoutBlockCollection`, pero `build()` arranca procesando `page_data.get("raw_blocks", [])` (`list`). El Type Checker del Builder no valida la hidratación inicial desde `dict[str, Any]`.
* **C3-004 — Hardcoding de Perfil Documental en el Builder (`builder.py`) [P1]:**
  Inyecta `primary_language="en"` y un `document_type` estático al instanciar `DocumentLayout`, ignorando las inferencias producidas por el módulo `core/document_profile`.
* **C3-006 — Falsa Inmutabilidad Profunda en DTOs (`models.py`) [P1]:**
  Tanto `LayoutBlockDraft` como `InferredDocumentProfile` usan `ConfigDict(frozen=True)`, pero contienen atributos mutables como `merge_history: List[str]` y `blocks: List[LayoutBlockDraft]`. Un consumidor puede ejecutar `obj.blocks.append(...)` sin violar Pydantic.
* **C3-007 — Telemetría Falsa ante Excepciones Inesperadas (`base.py`) [P1]:**
  `LayoutStage.process()` fija `status = "SUCCESS"` y solo lo cambia a `"FAILED"` si captura `DomainException`. Si se lanza un `KeyError`, `AttributeError` o `ValidationError`, la excepción atraviesa el bloque y el `finally` registra la ejecución en la telemetría como `status = "SUCCESS"`.
* **C3-008 — Type-Checking Runtime Limitado (`builder.py`) [P2]:**
  La validación `issubclass(current.OUTPUT_TYPE, next.INPUT_TYPE)` no valida payloads reales en runtime ni garantiza que las invariantes de dominio requeridas por la etapa posterior se hayan cumplido.

### 3.3 Inconsistencias de Taxonomía, Tipado e Identidad

* **C3-005 — Triplicación de Taxonomías Semánticas [P1]:**
  Coexisten `core.ast.enums.ContentNodeType`, `core.domain.document.LayoutBlockType` y cadenas libres `logical_type: Optional[str]`. No existe un mapa contractual de traducción entre ellas.
* **C3-009 — Tipo Semántico en Cadenas Libres (`classifier.py`) [P1]:**
  `LogicalClassifier` asigna tipos mediante cadenas literales (`"TITLE"`, `"PARAGRAPH"`). Si se produce un error tipográfico (`"PARAGRPAH"`), el sistema lo acepta silenciosamente.
* **C3-010 — Confusión entre `provider_native_id` y Tipo Semántico (`classifier.py`) [P1]:**
  `_resolve_from_provider()` hace `if "TITLE" in pid: return "TITLE"`. Infiere el tipo semántico a partir de la subcadena del identificador del bloque nativo (`block_91827`), confundiendo identidad con tipo.
* **C3-017 — Identidad de Bloque Acoplada al Proveedor (`identity.py`) [P1]:**
  La semilla del hash en `BlockIdentityGenerator` incluye `context.provider.name`. Dos extractores (PyMuPDF y Docling) procesando exactamente el mismo bloque físico producirán `BlockId`s diferentes, inutilizando el hash para comparaciones de benchmark.
* **C3-018 — Corrupción de Identidad Content-Addressed post-Merge (`merger.py`) [P0 - CRÍTICO]:**
  El `block_id` se genera como el hash SHA-256 del contenido y BoundingBox iniciales. Cuando `SpatialMerger` fusiona dos bloques, actualiza `bbox` y `content`, pero mantiene el `block_id` de `b1` sin regenerar el hash. El ID resultante ya no corresponde al estado del bloque.

### 3.4 Defectos Algorítmicos y Heurísticos

* **C3-011 — Regex Matemática con Falsos Positivos (`classifier.py`) [P1]:**
  La expresión regular de matemática analiza asignaciones genéricas `[a-zA-Z0-9...]+\s*=\s*.+$`. Código como `x = foo()` o `result = calculate()` se clasifica como `DISPLAY_EQUATION` antes de llegar al clasificador de código.
* **C3-012 — Declaración Falsa de Complejidad $O(1)$ (`classifier.py`) [P2]:**
  El código afirma ejecutar la clasificación en $O(1)$. La evaluación de expresiones regulares sobre texto depende de la longitud de la cadena ($O(N \cdot \text{longitud})$).
* **C3-013 — Asunción Implícita de Coordenadas Normalizadas (`detector.py`) [P1]:**
  `SpatialAnalyzer` calcula `int(block.bbox.x0 * bin_resolution)` asumiendo $x_0 \in [0, 1]$. Si la etapa `CoordinateNormalizer` no se ejecutó previamente, las coordenadas absolutas (ej. $x_0 = 72.0$) destruyen el histograma.
* **C3-014 — Descalce de Columnas entre Detector y Profile (`detector.py`) [P1]:**
  `SpatialAnalyzer` puede detectar 3 o más columnas mediante canales (*gutters*), pero `PageLayout` solo define `SINGLE_COLUMN`, `DOUBLE_COLUMN` y `UNKNOWN` (al haber removido `MULTI_COLUMN`).
* **C3-015 — Discrepancia entre Documentación y Código en Gutters (`detector.py`) [P2]:**
  El docstring afirma filtrar valles con un ancho mínimo del 3% ($0.03$), pero el código ejecuta `(gutters[i + 1] - current) < 0.04` (4%).
* **C3-016 — Etiqueta Arbitraria "Sturges-Steward" (`detector.py`) [P2]:**
  La fórmula `max(100, min(512, int(len(blocks) * 3.5)))` se etiqueta en el código como "regla Sturges-Steward", cuando en realidad es una constante empírica no estándar.
* **C3-019 — Discrepancia Topológica en `SpatialMerger` (`merger.py`) [P1]:**
  `SpatialAnalyzer` calcula el `column_index` dinámico por histograma, pero `SpatialMerger` re-clasifica las columnas mediante un pivote estático `b.bbox.x0 > 0.45`.
* **C3-020 — Fusión Limitada a Adyacencia en Lista (`merger.py`) [P1]:**
  El bucle de fusión solo evalúa el bloque adyacente en la lista ordenada. Si un bloque $B$ se interpone geométricamente entre $A$ y $C$, la fusión legítima entre $A$ y $C$ es descartada.
* **C3-021 — Falsa Validación de DAG (`reading_order.py`) [P1]:**
  El método `_validate_dag_integrity()` afirma realizar una "validación de integridad del DAG", pero su código solo elimina auto-bucles (`if node in edges: edges.remove(node)`). No ejecuta algoritmos de ciclos (Tarjan/Kahn) ni valida que sea un DAG real.
* **C3-022 — Complejidad Reclamada vs. Real en Sweep-Line (`reading_order.py`) [P1]:**
  Se afirma un rendimiento $O(n \log n)$, pero la actualización del `active_set` ejecuta una comprensión de listas completa sobre todos los elementos en cada iteración, derivando en un peor caso $O(n^2)$.
* **C3-023 — Conversión Implícita de `None` a Columna 0 (`reading_order.py`) [P1]:**
  El código usa `b.column_index or 0`. Asimila una columna no determinada (`None`) con la primera columna física (`0`), forzando una precedencia espacial incorrecta.
* **C3-024 — Criterio Arbitrario para Romper Ciclos (`reading_order.py`) [P1]:**
  Al detectar ciclos en el grafo, se aplica un desempate por el mapa estático `TYPE_PRIORITY` (`TITLE: 0`, `EQUATION: 1`, `CODE: 2`, `PARAGRAPH: 3`). Forzar que una ecuación siempre preceda al texto en un ciclo es una heurística arbitraria que puede alterar el orden real.
* **C3-025 — Clamping Silencioso en Normalización (`normalizer.py`) [P1]:**
  `_scale_and_clamp()` aplica `max(0.0, min(val, 1.0))`. Si un extractor emite una coordenada corrupta ($x_0 = 1.15$ o $x_0 = -0.1$), el normalizador la repara silenciosamente a $1.0$ y $0.0$, ocultando la anomalía al sistema de observabilidad.
* **C3-026 — Riesgo de Doble Normalización (`normalizer.py`) [P1]:**
  El normalizador no verifica `bbox.is_normalized`. Si recibe un bloque ya normalizado, vuelve a dividir por `page_width` y `page_height`, corrompiendo las dimensiones.

### 3.5 Defectos en Validación y Document Profile

* **C3-027 — Cobertura Limitada en `DocumentLayoutValidator` (`validator.py`) [P1]:**
  Solo valida existencia de páginas, monotonicidad, unicidad de IDs y dimensiones no negativas. Ignora coherencia de `total_pages == len(pages)`, límites fuera de página y consistencia del `column_index`.
* **C3-028 — Colapso por `AttributeError` en Validadores (`validator.py`) [P1]:**
  El validador hace `str(block.block_id.value)` sin verificar `block.block_id is not None`. Si recibe un bloque corrupto sin ID, la barrera defensiva colapsa con `AttributeError` en lugar de emitir un informe de invalidez.
* **C3-029 — Puntuación Negativa en Classifiers (`scoring.py`) [P1]:**
  En `ClassificationScores.winner()`, si `best_score` es un número negativo (ej. `-0.4`), el método retorna `(best_type, -0.4)`, emitiendo una confianza matemática negativa inválida.
* **C3-030 — Falsa Probabilidad en Calificación (`scoring.py`) [P1]:**
  Se ejecuta `min(best_score, 1.0)` sobre la suma acumulada de puntuaciones. Acumular $1.7$ puntos y truncarlos a $1.0$ no constituye una distribución de probabilidad ni una métrica de confianza calibrada.
* **C3-031 — Sobrecarga Semántica de `PageLayout.UNKNOWN` (`models.py`) [P2]:**
  `UNKNOWN` se emite indistintamente por falta de bloques, falla del extractor geométrico o confianza cero. Se confunden los errores de infraestructura con los diagnósticos de dominio.
* **C3-032 — Muestreo no Representativo en `ProfileSamplingPolicy` (`profiler.py`) [P1]:**
  `HeuristicDocumentProfiler` evalúa el layout analizando solo los primeros $N$ nodos del muestreo. Si el muestreo toma solo párrafos de la página 1, clasificará como `SINGLE_COLUMN` un documento que es de doble columna a partir de la página 2.
* **C3-033 — Ausencia de Linaje en `ProfileStore` (`ports.py`) [P2]:**
  La interfaz `ProfileStore.save(document_id, profile)` descuida el hash del documento, la versión del extractor y la versión de la política. Un perfil calculado para el PDF v1 puede reutilizarse por error sobre el PDF v2.

---

## 4. ANATOMÍA Y BATERÍA DEL GOLDEN REGRESSION FUTURO

Para erradicar la tautología ($A == A$), el sistema de regresión del **Hito 0.5** debe desacoplar la generación del oráculo respecto a la prueba de integración.

```text
[ ESTRUCTURA DEL GOLDEN REGRESSION GATE CANÓNICO ]

                 ┌───────────────────────────┐
                 │   Corpus PDF Inmutable    │
                 └─────────────┬─────────────┘
                               │
                               ▼
                 ┌───────────────────────────┐
                 │  Extraction Provider Real │
                 │    (PyMuPDF / Docling)    │
                 └─────────────┬─────────────┘
                               │
                               ▼
                 ┌───────────────────────────┐
                 │   DocumentLayoutBuilder   │
                 └─────────────┬─────────────┘
                               │
                               ▼
                 ┌───────────────────────────┐
                 │      FlatASTBuilder       │
                 └─────────────┬─────────────┘
                               │
                               ▼
                 ┌───────────────────────────┐
                 │       AST V2 Real         │
                 └─────────────┬─────────────┘
                               │
                               ▼
                 ┌───────────────────────────┐
                 │   ASTFingerprintPolicy    │
                 └─────────────┬─────────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
     Current Runtime Vector        Golden Fingerprint (JSON)
     (Calculado en memoria)        (Congelado en disco)
                │                             │
                └──────────────┬──────────────┘
                               │
                               ▼
                 ┌───────────────────────────┐
                 │   Aserción Estricta       │
                 │   CURRENT == EXPECTED     │
                 └───────────────────────────┘
```

### Anatomía de los 7 Niveles del Golden Fingerprint
El oráculo de regresión debe incluir las siguientes dimensiones inmutables:

1. **Nivel 1 (Volumétrico):** `total_pages`, `total_blocks`, `total_ast_nodes`.
2. **Nivel 2 (Semántico):** Distribución exacta por `ContentNodeType`.
3. **Nivel 3 (Secuencial):** Secuencia ordenada de tipos de nodos (`heading` $\rightarrow$ `paragraph` $\rightarrow$ `display_equation`).
4. **Nivel 4 (Geométrico):** BoundingBox normalizado $[x_0, y_0, x_1, y_1]$ e índice de columna por bloque con precisión de 3 decimales.
5. **Nivel 5 (Estructural):** Linaje de anidamiento (`depth`, `parent_node_id`, `segment_index`).
6. **Nivel 6 (Contenido):** Hash SHA-256 del contenido normalizado y longitud textual.
7. **Nivel 7 (Identidad):** `canonical_block_id` (independiente del nombre del proveedor).

### Distinción Fundamental: Golden Regression vs. Benchmark
* **Golden Regression:** Responde a *"¿El pipeline actual alteró la salida respecto a la versión previamente aceptada?"* Es un pase/fallo determinista de CI.
* **Benchmark:** Responde a *"¿Qué extractor (PyMuPDF vs. Docling vs. Marker) reconstruye con mayor precisión el Ground Truth?"* Es una evaluación científica comparativa exógena.

---

## 5. MARCO NORMATIVO: REGLAS FUTURAS Y PROHIBICIONES (C3-R01 A C3-R15)

Las siguientes reglas forman el contrato técnico de cumplimiento obligatorio para el **Hito 0.5** y la **Fase 17**:

### REGLAS DE OBLIGATORIO CUMPLIMIENTO (SÍ HACER)
* **C3-R01 (Golden Independiente):** El *Golden Fingerprint* debe ser generado externamente mediante la CLI `generate_golden` y guardado en disco. Las pruebas deben ser de solo lectura.
* **C3-R02 (Pruebas con Componentes Reales):** Las pruebas de integración deben procesar PDFs reales sin aplicar `patch.object` sobre los métodos principales de extracción.
* **C3-R03 (Contrato de Espacio de Coordenadas):** Cada etapa de layout debe declarar explícitamente si exige un espacio de coordenadas `ABSOLUTE` o `NORMALIZED`.
* **C3-R04 (Regeneración de Hash post-Merge):** Si `SpatialMerger` modifica el contenido o el BoundingBox de un bloque, debe recalcular el `block_id` para preservar la semántica del hash *content-addressed*.
* **C3-R05 (Unicidad de Topología):** Una vez que `SpatialAnalyzer` calcula el `column_index`, las etapas posteriores (`SpatialMerger`, `ReadingOrderResolver`) deben consumir dicho valor como la única fuente de verdad.
* **C3-R06 (Aislamiento de Diagnóstico en Excepciones):** `LayoutStage.process()` debe marcar la telemetría como `"FAILED"` ante cualquier excepción no controlada (`Exception`), registrando la traza original sin alterar la falla.
* **C3-R07 (Inmutabilidad Profunda en DTOs):** Reemplazar las colecciones mutables (`List`, `Dict`) dentro de DTOs con `frozen=True` por estructuras inmutables (`tuple`, `MappingProxyType`).
* **C3-R08 (Canonicalización de Tipos):** Sustituir el uso de cadenas libres `logical_type: Optional[str]` por la enumeración fuertemente tipada `LayoutBlockType`.
* **C3-R09 (Separación de Identidad):** Separar el metadato `provider_native_id` de la identidad canónica del bloque `canonical_block_id`.
* **C3-R10 (Batería de Pruebas Algorítmicas):** Diseñar e implementar pruebas unitarias dedicadas e independientes para `CoordinateNormalizer`, `LogicalClassifier`, `SpatialAnalyzer`, `BlockIdentityGenerator`, `SpatialMerger` y `ReadingOrderResolver`.

### PROHIBICIONES ABSOLUTAS (QUÉ NO HACER)
* ❌ **PROHIBIDO** escribir `expected_fingerprint = current_fingerprint` o generar la expectativa desde el runtime dentro de la ejecución de una prueba.
* ❌ **PROHIBIDO** parchear `adapter.parse` y nombrar la prueba "Real Parser Test".
* ❌ **PROHIBIDO** crear archivos de texto con el encabezado `%PDF-1.4 Dummy` y utilizarlos como sustitutos de binarios PDF reales.
* ❌ **PROHIBIDO** utilizar la expresión `x or 0` cuando $0$ es un valor semántico válido (ej. primera columna) y `None` representa ausencia de dato.
* ❌ **PROHIBIDO** aplicar `clamp` silencioso a coordenadas fuera de margen sin registrar un evento de diagnóstico en la telemetría.
* ❌ **PROHIBIDO** sobreprometer propiedades algorítmicas en docstrings (ej. afirmar validaciones DAG o eficiencias $O(n \log n)$) que el código no implemente.

---

## 6. PLAN DE SANEAMIENTO Y REMEDIACIÓN SECUENCIAL (C3-FUTURE-01 A C3-FUTURE-10)

La remediación no debe ejecutarse de forma caótica. Se fija el siguiente orden de dependencia para las fases posteriores:

```text
[ PLAN DE REMEDIACIÓN TÉCNICA C3-FUTURE ]

1. C3-FUTURE-01 ──► Reparar test_golden_parser.py y test_real_parser_pipeline.py.
2. C3-FUTURE-02 ──► Congelar un corpus de fixtures PDF reales (1 col, 2 col, tablas, fórmulas).
3. C3-FUTURE-03 ──► Crear la herramienta CLI explícita de generación/congelamiento del Golden.
4. C3-FUTURE-04 ──► Centralizar la política de huella digital utilizando ASTFingerprintPolicy.
5. C3-FUTURE-05 ──► Definir la semántica de identidad canónica vs. identidad de proveedor.
6. C3-FUTURE-06 ──► Establecer el contrato formal de espacios de coordenadas (Absolute/Normalized).
7. C3-FUTURE-07 ──► Consolidar las taxonomías LayoutBlockType y ContentNodeType.
8. C3-FUTURE-08 ──► Implementar la batería de unit tests aislados para cada etapa del Layout.
9. C3-FUTURE-09 ──► Conectar DocumentLayoutBuilder a la ingesta física de ExtractionProviders.
10. C3-FUTURE-10 ──► Ejecutar el benchmark topológico empírico sobre el corpus real.
```

---

## 7. DISPOSICIÓN RECOMENDADA DE ARCHIVOS DEL BLOQUE C3

| Módulo / Archivo | Estado Recomendado | Directiva de Gobernanza |
| :--- | :---: | :--- |
| `core/document_profile/*` | **KEEP** | Mantener arquitectura de ports/protocols; refactorizar `scoring.py` y añadir unit tests. |
| `core/layout/*` | **FREEZE AS-IS** | Conservar la base algorítmica; sanear `merger.py` (IDs) y `base.py` (telemetría) en Hito 0.5. |
| `test_layout_validator.py` | **KEEP & EXTEND** | Conservar como prueba base; ampliar la cobertura hacia geometrías normalizadas. |
| `test_real_parser_pipeline.py` | **REWRITE FUTURE** | Convertir de prueba simulada a un *Contract Test* real del adaptador. |
| `test_golden_parser.py` | **REWRITE FUTURE (P0)** | Prioridad absoluta: eliminar la tautología y conectar con el oráculo inmutable. |

---

## 8. EVALUACIÓN DE CONFIABILIDAD Y DECLARACIÓN DE CIERRE

### 8.1 DIAGNÓSTICO DE CONFIABILIDAD REAL
1. **Modelos y Abstracciones de Layout / Profile:** **ACEPTABLE / PROMETEDOR.**
   La estructura de clases, puertos y separación entre vista física y perfil documental es conceptualmente correcta y alineada con DDD.
2. **Implementación Algorítmica Espacial:** **AVANZADA PERO CON INCONSISTENCIAS.**
   Los algoritmos de histograma, fusión y ordenamiento por grafos poseen un nivel técnico elevado, pero presentan brechas como la corrupción de hashes en fusiones y discrepancias de pivot.
3. **Barrera de Regresión y Pruebas Automatizadas:** **FALSA / CORRUPTA.**
   Debido a las tautologías y parches masivos, la suite actual es incapaz de detectar fallas o degradaciones en la maquetación.

---

### 8.2 DECISIÓN FINAL DEL SUB-HITO 0.4.4-C3

The audit for **Block C3 (Layout Regression & Document Profile)** is hereby declared **CLOSED**.

```text
====================================================================================
                  ESTADO DE AUDITORÍA: SUB-HITO 0.4.4-C3
====================================================================================
  Audit Status             | CLOSED (Auditoría Finalizada)
  Code Remediation         | DEFERRED (Diferido a Hito 0.5)
  Production Certification | NOT GRANTED (Requiere remediación de tests y contratos)
  Remediation Backlog      | OPEN (Reglas C3-R01 a C3-R15 y C3-FUTURE-01 a 10)
====================================================================================
```

**Bitácora de Gobernanza:**
> *"Se da por concluida la auditoría del Bloque C3. Se confirma que el subsistema de maquetación (core/layout/*) y perfilado (core/document_profile/*) posee una arquitectura base sólida pero padece de desconexión en runtime, inconsistencias en la preservación de identidades post-fusión y una suite de regresión tautológica que invalida la detección de errores. No se realizaron cambios en código durante C3. Los hallazgos se trasladan al Hito 0.5 como Backlog de Remediación Obligatorio, priorizando la restauración de la honestidad de los Golden Tests antes de proceder al congelamiento de la línea de base."*













"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""












# HITO_0.4.4_C4_COMPILER_SERIALIZATION_AUDIT.md
## Compiler Pipeline, LaTeX Rendering, Tectonic Execution, Log Parsing & AST Serialization — Reporte Consolidado Bloque C4

* **Estado:** AUDIT CLOSED / REMEDIATION BACKLOG OPEN (Bloque C4)
* **Fecha de Emisión:** 2026-07-28
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.4 (Sub-hito 0.4.4-C: Bloque C4)
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Auditoría analítica y forense estricta sobre la totalidad de la capa de reconstrucción de documentos, ensamblado, generación LaTeX, invocación del compilador Tectonic, parseo de logs y serialización/deserialización de ASTs (`core/compiler/*`, `apps/compiler/*`, `infra/serialization/ast_json.py`, `tools/evaluation/infrastructure/ast_deserializer.py`, `experiments/loaders/ast_json_loader.py`). Cero mutaciones en código productivo. Disposición diferida al Hito 0.5.

---

## 1. RESUMEN EJECUTIVO Y VEREDICTO ARQUITECTÓNICO

El Bloque C4 queda **AUDITADO Y REGISTRADO**, pero **NO SE CONSIDERA APTO PARA FREEZE NI APROBADO PARA PRODUCCIÓN.**

El análisis forense confirma que el Bounded Context de compilación posee una abstracción de renderizado sofisticada (`RenderContext`, `RenderStrategy`, `TexBuilder`) y un motor de serialización atómica excepcional (`infra/serialization/ast_json.py`). Sin embargo, **existen fallas de arquitectura críticas en la tubería de ejecución, contratos de dominio duplicados y falsas garantías de seguridad**:

1. **Falla de Doble Reconstrucción:** `DocumentAssembler` construye un objeto `ReconstructedDocument` que `CompilationService` descarta de inmediato para volver a reconstruir los payloads desde el repositorio, violando SRP y duplicando I/O.
2. **Degradación Silenciosa vs. Fail-Fast:** Ante la falta de linaje entre un chunk y el AST, el servicio crea nodos artificiales (`orphan_*`) para forzar la compilación en lugar de interrumpir el pipeline con `ASTConsistencyError`.
3. **Falsa Inmutabilidad y No-Determinismo:** DTOs congelados contienen listas y diccionarios mutables nativos, y los reportes de auditoría inyectan marcas de tiempo físicas (`time.time()`) que rompen la reproducibilidad.
4. **Contratos Engañosos en Infraestructura:** `DockerRunner` no ejecuta Docker (invoca el binario local `tectonic`), contamina el sistema de archivos de proceso (`os.getcwd()`) y aplica sanitizaciones HTML desalineadas.
5. **Pérdida de Semántica $N:1$ y Deserialización Paralela:** `RenderUnitMapper` destruye información topológica al reducir $N$ nodos AST a un único nodo primario, mientras que `ast_deserializer.py` implementa un desempaquetado manual que ignora la validación de Pydantic v2.

---

## 2. REGISTRO DE EVIDENCIA FORENSE (E-0.4-361 A E-0.4-375)

### Evidencia E-0.4-361: Falla de Doble Ensamblado y Violación de SRP
* **Archivos Fuente:** `core/compiler/assembler.py` vs. `core/compiler/service.py`
* **Análisis Forense:** `DocumentAssembler.assemble()` valida secuencias, resuelve fallbacks vía SHA-256 y construye un `ReconstructedDocument`. Sin embargo, `CompilationService.compile_document()` ejecuta `decision = self._assembler.assemble(...)`, ignora `decision.document` y vuelve a iterar sobre `dispatch_result.outcomes` realizando llamadas repetidas a `self._payload_repository.get_verified_payload()`. 
* **Resultado:** Existen dos propietarios del mismo comportamiento de reconstrucción de texto, generando I/O duplicado y desacoplando el estado de aceptación del documento respecto a los datos renderizados.

---

### Evidencia E-0.4-362: Fallback Estructural Silencioso (`orphan_*`)
* **Archivo Fuente:** `core/compiler/service.py`
* **Análisis Forense:** Si un chunk no encuentra nodos asociados en el índice del AST (`nodes_by_chunk`), el servicio no arroja `ASTConsistencyError`. En su lugar, registra un *warning* en logs y crea un `RenderUnit` sintético: `RenderUnit(node_id=f"orphan_{outcome.chunk_id}", node_type=ContentNodeType.PARAGRAPH, content=text)`.
* **Resultado:** Un documento con corrupción de linaje puede compilar con éxito y producir un PDF aparentemente válido pero topológicamente incorrecto, ocultando la falla al benchmark.

---

### Evidencia E-0.4-363: Falsa Inmutabilidad Profunda en DTOs de Ensamblado
* **Archivo Fuente:** `core/compiler/assembler.py`
* **Análisis Forense:** `AssemblyReport` y `DocumentAssemblyDecision` están decorados con `@dataclass(frozen=True, slots=True)`. Sin embargo, contienen atributos mutables nativos: `failure_reasons: dict` y `failed_outcomes: List[ChunkOutcome]`.
* **Resultado:** Aunque la reasignación directa de atributos está bloqueada, cualquier consumidor puede modificar el estado interno in-place (ej. `decision.failed_outcomes.append(...)` o `report.failure_reasons["x"] = 1`), violando las garantías de inmutabilidad del dominio.

---

### Evidencia E-0.4-364: Inyección de Marcas de Tiempo en DTOs de Dominio
* **Archivo Fuente:** `core/compiler/assembler.py`
* **Análisis Forense:** `AssemblyReport` asigna de forma predeterminada `timestamp=time.time()`. 
* **Resultado:** Dos ejecuciones científicas idénticas sobre el mismo dataset producirán reportes con hashes y contenidos de auditoría diferentes, rompiendo el principio de determinismo e idempotencia.

---

### Evidencia E-0.4-365: Bug Semántico en `_build_rejection()`
* **Archivo Fuente:** `core/compiler/assembler.py`
* **Análisis Forense:** Al construir un reporte de rechazo, el método asigna `total_chunks=max(1, len(failed_outcomes))`. 
* **Resultado:** Si un documento con 100 chunks falla en 1 solo chunk no degradable, el reporte registrará `total_chunks = 1` y `total_failed = 1`, perdiendo la métrica del universo total procesado y corrompiendo la observabilidad.

---

### Evidencia E-0.4-366: Falso DockerRunner y Fuga al Filesystem
* **Archivo Fuente:** `apps/compiler/docker_runner.py`
* **Análisis Forense:** 
  * `DockerRunner` no invoca un contenedor Docker. Ejecuta directamente el binario del sistema host: `subprocess.run(["tectonic", "--untrusted", "doc.tex"])`.
  * Escribe archivos de log (`tectonic_crash.log`) y copia PDFs finales utilizando el directorio de trabajo del proceso (`os.getcwd()`). Esto provoca condiciones de carrera si múltiples trabajos se compilan concurrentemente en el mismo proceso.
  * Realiza limpieza silenciosa de caracteres invisibles (`re.sub(...)`) y decodificación manual de entidades HTML (`&lt;` $\rightarrow$ `<`), asumiendo responsabilidades de sanitización que pertenecen a etapas previas.

---

### Evidencia E-0.4-367: Parser Léxico Determinista de Errores (SOTA)
* **Archivo Fuente:** `apps/compiler/log_parser.py`
* **Análisis Forense:** `LogParser` analiza el `stderr` de Tectonic/XeTeX mediante expresiones regulares deterministas. Extrae el número de línea exacto (`(?:l\.|line\s+)(\d+)`) y clasifica las fallas en la enumeración `ErrorType` (`MATH_MODE`, `UNDEFINED_MACRO`, `UNBALANCED_ENV`, `UNBALANCED_BRACKETS`, `AMSMATH_TAG_ERROR`, `EMPTY_DOCUMENT`, `UNKNOWN`), aislando la ventana de contexto relevante (`_extract_context`).

---

### Evidencia E-0.4-368: Duplicación Especular de Lógica LaTeX
* **Archivos Fuente:** `core/compiler/rendering/implementations.py` vs. `core/compiler/rendering/latex_utils.py`
* **Análisis Forense:** Se confirma un $100\%$ de duplicación de código. `LatexEscaper` (con la tabla de traducción `str.maketrans`) y `LatexPreambleBuilder` están reescritos de forma idéntica en ambos módulos.

---

### Evidencia E-0.4-369: Escapado LaTeX Ciego al Contexto
* **Archivo Fuente:** `core/compiler/rendering/implementations.py` (`LatexEscaper`)
* **Análisis Forense:** `LatexEscaper.escape()` sustituye ciegamente caracteres especiales (`\`, `&`, `%`, `$`, `{`, `}`). Si un texto contiene comandos o entornos LaTeX legítimos que entraron por el canal de traducción (ej. `\textbf{enunciado}` o `$E=mc^2$`), el escaper los convierte en `\textbackslash{}textbf\{enunciado\}` y `\$E=mc\^2\$`, destruyendo la sintaxis y provocando errores de compilación en Tectonic.

---

### Evidencia E-0.4-370: Pérdida de Información de Assets en AdaptiveFloatStrategy
* **Archivo Fuente:** `core/compiler/rendering/implementations.py`
* **Análisis Forense:** `RenderUnit` contiene el Value Object `asset: Optional[AssetReference]`. Sin embargo, `AdaptiveFloatStrategy.render()` lee únicamente `unit.content` y jamás consulta `unit.asset.path` ni `unit.asset.alt_text`. La referencia al recurso multimedia es información muerta (*dead data*) en la etapa de renderizado.

---

### Evidencia E-0.4-371: Reducción Colisionante $N:1$ en `RenderUnitMapper`
* **Archivo Fuente:** `core/compiler/rendering/mapper.py`
* **Análisis Forense:** Cuando un chunk abarca $N$ nodos AST, `DefaultRenderUnitMapper` selecciona el nodo con mayor prioridad semántica (`_TYPE_PRIORITY`) como `primary_node` y le asigna su `node_type` y `geometry` al `RenderUnit`. Si un chunk contiene un título, un párrafo y una fórmula, el `RenderUnit` final asumirá el tipo de la fórmula, destruyendo la jerarquía de los otros nodos del grupo.

---

### Evidencia E-0.4-372: Escritura Atómica en Disco de Grado SRE (SOTA)
* **Archivo Fuente:** `infra/serialization/ast_json.py`
* **Análisis Forense:** `write_ast_json_atomic()` implementa la máxima garantía de persistencia física: utiliza `TypeAdapter(List[ASTNode])` de Pydantic v2, escribe en un archivo efímero en la misma carpeta, fuerza el vaciado físico a disco mediante `os.fsync(tf.fileno())` y realiza un reemplazo atómico de puntero en el kernel del sistema operativo vía `temp_path.rename()`.

---

### Evidencia E-0.4-373: Deserialización Manual que Bypassea Pydantic (P0 - CRÍTICO)
* **Archivo Fuente:** `tools/evaluation/infrastructure/ast_deserializer.py`
* **Análisis Forense:** A diferencia de `infra/serialization/ast_json.py`, `ASTJsonDeserializer` desempaca diccionarios a mano (`ASTNode(**clean_kwargs)`) tras filtrar claves. Esto ignora las validaciones avanzadas de discriminación de payloads (`@model_validator(mode="before")`), arriesgando la rehidratación de nodos soplados o inconsistentes durante la ejecución del benchmark.

---

## 3. ANÁLISIS DE IMPACTO Y ARQUITECTURA DE DOMINIO

### 3.1 La Falla del Pipeline de Compilación: Flujo Actual vs. Flujo Canónico

El análisis forense demuestra que el compilador sufre una desconexión en la transferencia de responsabilidad:

```text
[ FLUJO ACTUAL EN TIEMPO DE EJECUCIÓN (CON DUPLICACIÓN Y DESCARTES) ]

                ┌──────────────────┐
                │  DispatchResult  │
                └────────┬─────────┘
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
┌──────────────────┐             ┌──────────────────┐
│ DocumentAssembler│             │CompilationService│
└───────┬──────────┘             └────────┬─────────┘
        │                                 │
        ▼                                 │ (Vuelve a recuperar payloads)
ReconstructedDocument                     ▼
   (DESCARTADO ✗)                  RenderUnitMapper
                                          │
                                          ▼
                                     TexBuilder
```

```text
[ FLUJO CANÓNICO REQUERIDO (SINGLE SOURCE OF TRUTH) ]

DispatchResult ──► DocumentAssembler ──► AssembledDocument (Contenido + Linaje) ──► CompilationService ──► RenderUnitMapper ──► TexBuilder ──► TectonicRunner
```

---

## 4. TAXONOMÍA Y MATRIZ DE AUDITORÍA FORENSE DE COMPONENTES (C4)

```text
[ CLASIFICACIÓN DE COMPONENTES DEL BLOQUE C4 ]

1. ARQUITECTURA SOTA ESTABILIZADA (CONSERVAR):
   ├── apps/compiler/tex_builder.py (TexBuilder IoC con comentarios de Node ID)
   ├── apps/compiler/log_parser.py (LogParser determinista para stderr de Tectonic)
   ├── core/compiler/rendering/context.py (RenderContextFactory, Strategy Mapping)
   ├── core/compiler/rendering/policies.py (DocumentStructurePolicy, RenderStrategy)
   ├── infra/serialization/ast_json.py (Persistencia atómica con fsync + TypeAdapter)
   └── experiments/loaders/ast_json_loader.py (Carga de secuencias reutilizando infra)

2. DEUDA ARQUITECTÓNICA Y REFACTORIZACIÓN (REMEDIAR EN HITO 0.5):
   ├── core/compiler/assembler.py (Contrato de inmutabilidad, determinismo y _build_rejection)
   ├── core/compiler/service.py (Eliminar re-ensamblado manual y fallback de nodos huérfanos)
   ├── apps/compiler/docker_runner.py (Renombrar a TectonicRunner, aislar I/O de os.getcwd())
   ├── core/compiler/rendering/implementations.py (LatexEscaper Context-Aware y uso de Assets)
   └── core/compiler/rendering/mapper.py (Cálculo de envolvente espacial para chunks N:1)

3. ARTEFACTOS DUPLICATED O DESALINEADOS (ELIMINAR / UNIFICAR):
   ├── core/compiler/rendering/latex_utils.py (Duplicado 100% -> Re-exportar desde implementations)
   └── tools/evaluation/infrastructure/ast_deserializer.py (Bypassea Pydantic v2 -> Reutilizar ast_json)
```

| Componente / Archivo | Categoría | Inmutabilidad / Tipeado | Riesgo de Regresión | Disposición Hito 0.5 |
| :--- | :--- | :--- | :---: | :--- |
| `apps/compiler/docker_runner.py` | Infrastructure | Impura (Escribe en `getcwd`) | **Alto** | **RENOMBRAR Y AISLAR I/O** |
| `apps/compiler/log_parser.py` | Log Parsing | Pydantic v2 / Regex | Bajo | **CONSERVAR** |
| `apps/compiler/tex_builder.py` | Rendering | IoC Pure Class | Bajo | **CONSERVAR** |
| `compiler/assembler.py` | Core Domain | Falsa inmutabilidad en DTOs | **Alto** | **REFACTORIZAR (C4-A)** |
| `compiler/exceptions.py` | Domain Errors | Custom Exceptions | Bajo | **CONSERVAR** |
| `compiler/service.py` | Application | Duplica lógica de Assembler | **P0 (Crítico)** | **REFACTORIZAR OBLIGATORIO** |
| `compiler/rendering/context.py` | Rendering | Frozen Dataclasses / Slots | Bajo | **CONSERVAR** |
| `compiler/rendering/implementations.py`| Rendering | Escaper ciego / Assets muertos| Medio | **REFACTORIZAR ESCAPER/ASSETS** |
| `compiler/rendering/latex_utils.py` | Duplicado | Copia $100\%$ idéntica | **P1 (Deuda)** | **ELIMINAR / RE-EXPORTAR** |
| `compiler/rendering/mapper.py` | Mapping | Pérdida de semántica $N:1$ | Medio | **MEJORAR ENVOLVENTE** |
| `compiler/rendering/models.py` | DTOs | Frozen Dataclasses / Slots | Bajo | **CONSERVAR** |
| `compiler/rendering/policies.py` | Protocols | Typing Protocol | Bajo | **CONSERVAR** |
| `infra/serialization/ast_json.py` | Serialization | Kernel Atomic / Pydantic v2 | **SOTA** | **ESTÁNDAR ÚNICO** |
| `ast_deserializer.py` | Deserializer | Unpacking manual sin Pydantic | **P0 (Riesgo)**| **UNIFICAR CON AST_JSON** |
| `ast_json_loader.py` | Experiment Loader | Thin Wrapper | Bajo | **CONSERVAR** |

---

## 5. MARCO NORMATIVO Y BACKLOG DE REMEDIACIÓN FUTURA (C4-R01 A C4-R16)

Las modificaciones de código quedan prohibidas durante la Fase 0. Las siguientes reglas constituyen el contrato de cumplimiento obligatorio para el **Hito 0.5** y la **Fase 17**:

### REGLAS DE OBLIGATORIO CUMPLIMIENTO (SÍ HACER)
* **C4-R01 (Propietario Único de Reconstrucción):** `DocumentAssembler` debe ser el único componente encargado de reconstruir el contenido de los chunks y resolver fallbacks. `CompilationService` debe consumir exclusivamente el `AssembledDocument` retornado por el ensamblador, eliminando el acceso duplicado a `payload_repository`.
* **C4-R02 (Principio Fail-Fast en Linaje AST - P0):** Si un chunk carece de linaje en el AST, `CompilationService` debe interrumpir el proceso arrojando `ASTConsistencyError`. Queda estrictamente prohibida la generación de nodos sintéticos `orphan_*`.
* **C4-R03 (Inmutabilidad Profunda Real):** Reemplazar las colecciones mutables (`List`, `dict`) dentro de `AssemblyReport` y `DocumentAssemblyDecision` por tipos inmutables (`tuple`, `MappingProxyType`, `FrozenSet`).
* **C4-R04 (Determinismo en Artefactos de Auditoría):** Separar las métricas de dominio deterministas de la telemetría operacional. El campo `timestamp` en `AssemblyReport` debe ser inyectado por la capa de aplicación o aislado en un evento de telemetría externo.
* **C4-R05 (Corrección Semántica en Reportes de Rechazo):** El método `_build_rejection()` de `DocumentAssembler` debe registrar el total real de chunks del trabajo (`total_chunks`), no la cantidad de fallos.
* **C4-R06 (Saneamiento de la Invocación del Compilador):** Renombrar `DockerRunner` a `TectonicRunner` (o implementar una ejecución en contenedor real). Toda la I/O de compilación (`output.pdf`, `tectonic_crash.log`) debe generarse dentro de un directorio efímero aislado (`tempfile.TemporaryDirectory()`), prohibiendo escrituras en `os.getcwd()`.
* **C4-R07 (Eliminación de Sanitización Silenciosa):** Retirar la decodificación de entidades HTML y la purga de caracteres del ejecutor del compilador. La sanitización debe ocurrir en las etapas de entrada upstream.
* **C4-R08 (Consolidación de Serialización AST - P0):** Eliminar la deserialización manual de `tools/evaluation/infrastructure/ast_deserializer.py`. Todos los módulos del repositorio deben deserializar ASTs utilizando exclusivamente `infra/serialization/ast_json.py` (`deserialize_ast_json`).
* **C4-R09 (Eliminación de Duplicación LaTeX):** Eliminar el código duplicado en `core/compiler/rendering/latex_utils.py`, convirtiéndolo en un módulo de re-exportación de `implementations.py`.
* **C4-R10 (Context-Aware LaTeX Escaper):** Diseñar un sanitizador de caracteres LaTeX que distinga entre texto plano que requiere escapado de caracteres especiales (`&`, `%`, `$`, `_`) y fragmentos con marcado TeX o entornos matemáticos válidos, evitando destruir comandos legítimos como `\textbf{}`.
* **C4-R11 (Materialización de AssetReference):** Actualizar `AdaptiveFloatStrategy.render()` para que consuma los metadatos de `unit.asset` (`path`, `alt_text`, `label`), generando bloques `\includegraphics` y etiquetas de figura válidas.
* **C4-R12 (Preservación de Semántica $N:1$):** Modificar `DefaultRenderUnitMapper` para que no restrinja el tipo y la geometría del `RenderUnit` a un único nodo primario, conservando la información de todos los nodos AST pertenecientes al chunk.

### PROHIBICIONES ABSOLUTAS (QUÉ NO HACER)
* ❌ **PROHIBIDO** que `CompilationService` vuelva a consultar `payload_repository` si `DocumentAssembler` ya ejecutó el ensamblado.
* ❌ **PROHIBIDO** generar nodos sintéticos (`orphan_*`) para ocultar la pérdida de linaje entre chunks y el AST.
* ❌ **PROHIBIDO** denominar `DockerRunner` a un componente que ejecuta binarios nativos en el sistema host.
* ❌ **PROHIBIDO** escribir logs de falla (`tectonic_crash.log`) o artefactos de salida en el directorio de trabajo del proceso (`os.getcwd()`).
* ❌ **PROHIBIDO** implementar deserializadores de AST paralelos mediante desempaquetado manual de diccionarios.

---

## 6. PLAN DE REMEDIACIÓN Y SANEAMIENTO SECUENCIAL (C4-FUTURE-01 A C4-FUTURE-08)

```text
[ PLAN DE REMEDIACIÓN TÉCNICA C4-FUTURE ]

1. C4-FUTURE-01 ──► Corregir el flujo de datos: Assembler emite AssembledDocument; Service consume sin re-ensamblar.
2. C4-FUTURE-02 ──► Aplicar Fail-Fast: Eliminar la creación de nodos orphan_* y lanzar ASTConsistencyError.
3. C4-FUTURE-03 ──► Unificar la deserialización de ASTs bajo infra/serialization/ast_json.py.
4. C4-FUTURE-04 ──► Renombrar DockerRunner a TectonicRunner y aislar I/O dentro del directorio temporal.
5. C4-FUTURE-05 ──► Eliminar la duplicación de código en core/compiler/rendering/latex_utils.py.
6. C4-FUTURE-06 ──► Inmutabilizar DTOs con tuples/MappingProxyType y corregir total_chunks en _build_rejection.
7. C4-FUTURE-07 ──► Desarrollar un LatexEscaper consciente del contexto y materializar AssetReference en el render.
8. C4-FUTURE-08 ──► Implementar la batería de unit tests aislados para Assembler, LogParser y RenderContext.
```

---

## 7. ARQUITECTURA INTEGRADA OBJETIVO DEL COMPILADOR (FASE 17 / 18)

```text
                       ┌─────────────────────────┐
                       │     DispatchResult      │
                       │   (Translated Chunks)   │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │    DocumentAssembler    │
                       ├─────────────────────────┤
                       │ 1. Sequence Validation  │
                       │ 2. SHA-256 Fallback Check│
                       │ 3. AssemblyPolicy Check │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │    AssembledDocument    │
                       │ (Single Source of Truth)│
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │   CompilationService    │
                       ├─────────────────────────┤
                       │ 1. AST Reconciler (1:N) │
                       │ 2. RenderUnitMapper     │
                       │ 3. RenderContextFactory │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │       TexBuilder        │
                       │  (LaTeX Source Gen)     │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │     TectonicRunner      │
                       │  (Isolated Temp Dir)    │
                       └────────────┬────────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
               (Success)                      (Failure)
                     │                             │
                     ▼                             ▼
           ┌──────────────────┐          ┌──────────────────┐
           │   Final PDF      │          │    LogParser     │
           │   Artifact       │          │ (ParsedError DTO)│
           └──────────────────┘          └──────────────────┘
```

---

## 8. EVALUACIÓN DE CONFIABILIDAD Y DECLARACIÓN DE CIERRE

### 8.1 DIAGNÓSTICO DE CONFIABILIDAD REAL
1. **Infraestructura de Serialización (`ast_json.py`):** **100% SOTA Y SEGURO.**
   Garantías SRE de vaciado a disco (`fsync`) y reemplazo atómico a nivel de kernel.
2. **Arquitectura de Renderizado y Parsing de Logs (`apps/compiler/*`):** **EXCELENTE BASE CON DEUDA MENOR.**
   `TexBuilder`, `RenderContext` y `LogParser` poseen un diseño modular impecable; requieren únicamente aislar la I/O del runner y eliminar duplicaciones.
3. **Orquestación y Reconstrucción de Ensamblado (`assembler.py` / `service.py`):** **REQUERIRÁ REFACTORIZACIÓN EN HITO 0.5.**
   Exige corregir el patrón de doble ensamblado y eliminar el fallback silencioso de nodos huérfanos.

---

### 8.2 DECISIÓN FINAL DEL SUB-HITO 0.4.4-C4

The audit for **Block C4 (Compiler + Serialization)** is hereby declared **CLOSED**.

```text
====================================================================================
                  ESTADO DE AUDITORÍA: SUB-HITO 0.4.4-C4
====================================================================================
  Audit Status             | CLOSED (Auditoría Finalizada)
  Code Remediation         | DEFERRED (Diferido a Hito 0.5)
  Production Certification | NOT GRANTED (Requiere unificación de deserialización y runner)
  Remediation Backlog      | OPEN (Reglas C4-R01 a C4-R12 y C4-FUTURE-01 a 08)
====================================================================================
```

**Bitácora de Gobernanza:**
> *"Se da por concluida la auditoría del Bloque C4. Se certifica que la arquitectura de renderizado y serialización posee un diseño conceptual altamente profesional, pero padece de una falla de doble ensamblado en el servicio de compilación, degradación silenciosa por nodos huérfanos y un ejecutor de Tectonic desalineado de su contrato de infraestructura. No se realizaron cambios en código durante C4. Los hallazgos se trasladan al Hito 0.5 como Backlog de Remediación Obligatorio."*













"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


















# HITO_0.4.4_C5_SNAPSHOTS_CI_GATES_AUDIT.md
## Snapshots, Golden Corpora, Deterministic Invariants & CI Enforcement — Reporte Consolidado Bloque C5

* **Estado:** AUDIT CLOSED / REMEDIATION BACKLOG OPEN (Bloque C5)
* **Fecha de Emisión:** 2026-07-28
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.4 (Sub-hito 0.4.4-C: Bloque C5)
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Auditoría analítica y forense estricta sobre la infraestructura de snapshots, fixtures, scripts de bootstrap, corpus de calibración, configuración de tooling (`pyproject.toml`) y automatización de CI (`.github/workflows/*`). Cero mutaciones en código productivo. Disposición diferida al Hito 0.5.

---

## 1. PROPÓSITO Y ALCANCE

El **Sub-hito 0.4.4 (Bloque C5)** audita la capacidad del repositorio para actuar como un **mecanismo de blindaje contra regresiones en integración continua (CI Gates)**. 

El objetivo central es examinar la efectividad real de los snapshots de empaquetado, la inmutabilidad de los oráculos de prueba (*Golden Corpora*), la validez de los fixtures deterministas y la presencia de canalizaciones automatizadas (*CI Workflows*) que impidan el *merge* de código que altere invariantes topológicas, estructurales o semánticas en la **Fase 17 (Extraction Engine Integration)** y la **Fase 17_BIS (Canonical Scientific Baseline)**.

---

## 2. REGISTRO DE EVIDENCIA FORENSE (E-0.4-381 A E-0.4-390)

### Evidencia E-0.4-381: Snapshot Real de Chunking con Auto-generación Silenciosa (GAP-C5-01)
* **Archivos Fuente:** `tests/integration/test_chunker_snapshot.py`, `tests/fixtures/sample_chunks.json`
* **Análisis Forense:** 
  * Se confirma la existencia de un test de snapshot funcional (`test_snapshot_verification`) que lee la caché de un AST (`sample_3_pages.pdf.ast.json`), ejecuta `build_semantic_chunks_as_units()` y lo compara contra `tests/fixtures/sample_chunks.json`.
  * **Defecto de Puerta (Anti-patrón de Auto-creación):** El test contiene la lógica: `if not os.path.exists(self.snapshot_path): json.dump(actual_snapshot, ...)`. Si la prueba se ejecuta en un entorno limpio sin la fixture, **genera el snapshot sobre la marcha y retorna PASS de forma transparente**. Un Regression Gate jamás debe aprobar la ejecución si el oráculo está ausente; la ausencia del baseline debe arrojar `FAIL` inmediatamente.

---

### Evidencia E-0.4-382: Sub-cobertura de Aserciones en Snapshot Payload (GAP-C5-02)
* **Archivo Fuente:** `tests/integration/test_chunker_snapshot.py`
* **Análisis Forense:** El objeto `actual_snapshot` serializa 11 campos por cada unidad traducible (`chunk_index`, `chunk_id`, `chunk_fingerprint`, `chunk_type`, `source_sequence_range`, `node_count`, `context_id`, `context_depth`, `target_payload`, `estimated_tokens`, `payload_sha256`). Sin embargo, el bucle de validación solo compara 4 atributos (`chunk_id`, `payload_sha256`, `target_payload`, `context_id`).
* **Impacto:** Mutaciones críticas en `chunk_fingerprint`, `source_sequence_range`, `node_count` o `estimated_tokens` no son detectadas por la prueba, dejando la topología parcialmente desprotegida.

---

### Evidencia E-0.4-383: Contexto de Coste Determinista Puro para Zhang-Shasha (SOTA)
* **Archivo Fuente:** `tests/fixtures/unit_cost_context.py`
* **Análisis Forense:** Implementación impecable del puerto `TreeEditCostContext` para las pruebas del motor topológico. Retorna costos unitarios fijos en tiempo constante $O(1)$: `deletion_cost = 1.0`, `insertion_cost = 1.0` y `substitution_cost = 0.0` si el contenido textual coincide exactamente (o `1.0` si difiere). Cero I/O, cero dependencias flotantes.

---

### Evidencia E-0.4-384: Herramienta de Bootstrap sin Semántica de Gate (GAP-C5-03)
* **Archivo Fuente:** `tests/helpers/bootstrap_translation_golden.py`
* **Análisis Forense:** `capture_golden_snapshots()` orquesta un pipeline falso (`FakeChunker`, `FakeDispatcher`) sobre `sample_3_pages.pdf` para congelar 3 artefactos en `tests/golden/`: `structure.json`, `latex.json` y `semantics.json`.
* **Diagnóstico:** Es una herramienta útil de *bootstraping* inicial, pero no constituye un *Regression Gate*. Si este script se invocara de forma automatizada dentro de las pruebas, sobreescribiría los oráculos con el estado runtime actual, destruyendo la inmutabilidad de la línea de base.

---

### Evidencia E-0.4-385: Tautología y Permisividad de Ignorado en Golden Parser (P0 - CRÍTICO)
* **Archivo Fuente:** `tests/integration/test_golden_parser.py`
* **Análisis Forense:**
  * **Tautología Reconfirmada:** La prueba invalida el oráculo al ejecutar `expected_fingerprint = current_fingerprint`, comparando el estado runtime contra sí mismo ($A == A$).
  * **Anti-patrón `skipTest`:** El método ejecuta `if not os.path.exists(self.fingerprint_path): self.skipTest(...)`. Como la carpeta `tests/golden/` no existe en el repositorio actual, el CI simplemente omite la prueba y reporta éxito (`SKIP -> PASS`). La ausencia de una barrera de regresión obligatoria jamás debe resultar en un paje silencioso.

---

### Evidencia E-0.4-386: Bounded Context de Ground Truth vs. Carpetas Ad-hoc
* **Archivos Fuente:** `core/benchmark/ground_truth/*`, `infra/fs/ground_truth_store.py`
* **Análisis Forense:** El repositorio posee un Bounded Context maduro para la gestión del oráculo canónico (`GroundTruthReaderPort`, `GroundTruthDraftWriterPort`, `SealGroundTruthUseCase`, `LoadGroundTruthUseCase`).
* **Diagnóstico:** Crear una carpeta ad-hoc `tests/golden/` duplicaría innecesariamente la responsabilidad del almacenamiento de referencias. Los *Regression Gates* deben consumir directamente el Ground Truth criptográficamente congelado (respaldado por SHA-256) desde `core/benchmark/ground_truth/`.

---

### Evidencia E-0.4-387: Descalce Volumétrico en el Corpus de Calibración
* **Archivos Fuente:** `tests/corpus/calibration_v1/*` (5 documentos) vs. Requisitos de Fase 17_BIS
* **Análisis Forense:** El repositorio contiene el conjunto de calibración `calibration_v1` con 5 documentos (`doc_01_single` a `doc_05_graph`) con sus respectivos Ground Truths y candidatos para PyMuPDF y Docling.
* **Brecha de Alcance:** El roadmap de la Fase 17_BIS exige un *Golden Corpus* de 20 a 30 documentos de alta varianza ( papers multi-columna, fórmulas densas, tablas complejas). El volumen actual (~5 documentos) es adecuado para calibración inicial, pero insuficiente para la certificación de la línea de base científica.

---

### Evidencia E-0.4-388: Pruebas de Integración Sintáctica y Estructural (SOTA)
* **Archivos Fuente:** `tests/integration/test_translation_structure.py`, `tests/integration/test_translation_technical.py`
* **Análisis Forense:** Suites de prueba que certifican la integridad del pipeline mediante el `MarkdownInspector`. Validan el balance de delimitadores LaTeX (`$`, `$$`, `\begin{...}`), la preservación de listas y la presencia de etiquetas estructurales.

---

### Evidencia E-0.4-389: Ausencia de Contrato de Tooling Declarativo (GAP-C5-04)
* **Evidencia del Proyecto:** Ausencia de `pyproject.toml` en el árbol de archivos auditado.
* **Análisis Forense:** El proyecto carece de una fuente centralizada y declarativa para la configuración de `pytest`, opciones de *test discovery*, *markers* de ejecución (`@pytest.mark.smoke`, `@pytest.mark.integration`), umbrales de cobertura de código (*coverage thresholds*), linters (`ruff`, `flake8`) y verificadores de tipo (`mypy`, `pyright`).

---

### Evidencia E-0.4-390: Ausencia de Automatización de Integración Continua (GAP-C5-05 - CRÍTICO)
* **Evidencia del Proyecto:** Ausencia del directorio `.github/workflows/` en el árbol auditado.
* **Análisis Forense:** No existe evidencia material de canalizaciones automatizadas (*CI Pipelines*) configuradas en el repositorio.
* **Impacto:** Aunque las pruebas unitarias y de integración pasen localmente en la máquina del desarrollador, **no existe una barrera de control remota (*Required Status Check*) que bloquee el merge de Pull Requests si una aserción de regresión falla.**

---

## 3. ANÁLISIS DE IMPACTO Y ARQUITECTURA DE DOMINIO

### 3.1 La Cadena Rota de Regresión: De la Prueba Local al Merge Bloqueado

El análisis forense evidencia que la cadena de autoridad para la protección del código está incompleta en su último tramo:

```text
[ LA CADENA DE AUTORIDAD DE REGRESIÓN (ESTADO ACTUAL) ]

  Corpus Canónico ──► Ground Truth (Sellado) ──► Test Snapshot ──► Pytest Local ──x──► CI Workflow ──x──► Merge Protection
                                                                                   │                     │
                                                                           (NO EVIDENCIADO)      (NO EVIDENCIADO)
```

Para dar por cumplidos los objetivos de la Fase 17_BIS, la canalización debe cerrarse de extremo a extremo:

```text
[ CANALIZACIÓN CANÓNICA DE FASE 17_BIS (CERRADA) ]

  Corpus Canónico ──► Sealed Ground Truth ──► Fingerprint Policy ──► Assertion Gate ──► GitHub Actions ──► Block Merge on Failure
```

---

## 4. TAXONOMÍA Y MATRIZ DE AUDITORÍA FORENSE DE COMPONENTES (C5)

```text
[ CLASIFICACIÓN DE COMPONENTES DEL BLOQUE C5 ]

1. COMPONENTES Y FIXTURES CONSOLIDADOS (CONSERVAR):
   ├── tests/fixtures/unit_cost_context.py (Contexto de costos unitarios deterministas para TED)
   ├── tests/fixtures/sample_chunks.json (Baseline físico de chunks)
   ├── tests/fixtures/sample_3_pages.pdf.ast.json (Fixture AST serializado)
   ├── tests/helpers/markdown_inspector.py (Inspector de sintaxis y estructuras Markdown/TeX)
   ├── tests/integration/test_translation_structure.py (Validación de integridades estructurales)
   └── tests/integration/test_translation_technical.py (Validación de tokens y balance TeX)

2. COMPONENTES DEFECTUOSOS O CON GAPS (REFACTORIZAR EN HITO 0.5):
   ├── tests/integration/test_chunker_snapshot.py (P0: Auto-creación de baseline + sub-aserción)
   ├── tests/integration/test_golden_parser.py (P0: Tautología A == A + skipTest ante oráculo ausente)
   └── tests/helpers/bootstrap_translation_golden.py (Aislar como herramienta CLI, no usar en CI)

3. INFRAESTRUCTURA Y CANALIZACIONES FALTANTES (CREAR EN HITO 0.5):
   ├── pyproject.toml (Configuración declarativa central de pytest, coverage y linters)
   └── .github/workflows/ci.yml (Workflow de GitHub Actions con bloqueos de merge)
```

| Componente / Artefacto | Categoría | Propósito en CI/CD | Riesgo de Regresión | Disposición Hito 0.5 |
| :--- | :--- | :--- | :---: | :--- |
| `test_chunker_snapshot.py` | Integration Test | Snapshot del empaquetador | **P0 (Crítico)** | **REFACTORIZAR** (Frail-Fast si falta snapshot) |
| `test_golden_parser.py` | Integration Test | Fingerprint del parser | **P0 (Crítico)** | **REESCRIBIR** (Cero tautología/skips) |
| `unit_cost_context.py` | Fixture | Costos unitarios de TED | **Cero** | **CONSERVAR** |
| `bootstrap_translation_golden`| Helper CLI | Bootstrap de baselines | Medio | **AISLAR** (Solo invocación manual) |
| `markdown_inspector.py` | Helper | Inspección de marcado | Bajo | **CONSERVAR** |
| `calibration_v1/` | Corpus | Ground Truth de 5 docs | Medio | **EXPANDIR** (Hacia 20-30 docs en F17_BIS) |
| `pyproject.toml` | Infrastructure | Configuración de tooling | **Alto** | **CREAR** (Centralizar pytest/coverage) |
| `.github/workflows/*` | CI Pipeline | Dynamic Merge Gate | **P0 (Crítico)** | **CREAR** (CI Automation Workflow) |

---

## 5. REGLAS NORMATIVAS Y BACKLOG DE REMEDIACIÓN FUTURA (C5-R01 A C5-R10)

Queda estrictamente prohibida la modificación de código durante la Fase 0. Las siguientes reglas constituyen el backlog técnico obligatorio de remediación para el **Hito 0.5** y la **Fase 17_BIS**:

* **C5-R01 (Semántica Fail-Fast en Snapshots - P0):** Si el archivo oráculo de un snapshot (ej. `sample_chunks.json`) no existe en disk durante la ejecución de la suite de pruebas, el test debe **fallar de forma inmediata (`FAIL`)**. Queda estrictamente prohibido que un test autogenere el archivo ausente y retorne `PASS`.
* **C5-R02 (Aserción Exhaustiva de Campos):** Modificar `test_chunker_snapshot.py` para que la comparación contra el snapshot verifique el $100\%$ de los campos del DTO (`chunk_index`, `chunk_fingerprint`, `chunk_type`, `source_sequence_range`, `node_count`, `context_depth`, `estimated_tokens`).
* **C5-R03 (Restauración de la Barrera Golden Parser - P0):** Reescribir `test_golden_parser.py`. Eliminar la reasignación `expected_fingerprint = current_fingerprint`. Si el archivo de la huella digital no existe, la prueba debe arrojar un error explícito de infraestructura de pruebas, prohibiendo el uso de `skipTest()`.
* **C5-R04 (Consolidación del Oráculo en Ground Truth):** Prohibir la creación de carpetas ad-hoc `tests/golden/` duplicadas. La fuente de verdad inmutable para las pruebas de regresión del parser debe ser consumida directamente desde el Bounded Context `core/benchmark/ground_truth/` respaldado por manifiestos SHA-256.
* **C5-R05 (Separación Estricta entre Bootstrap y Verificación):** Aplanar y aislar `bootstrap_translation_golden.py` y `generate_golden_draft.py` como scripts de utilidad exclusivamente ejecutables por CLI en fases de mantenimiento, asegurando que jamás se ejecuten durante la corrida de tests automatizados de CI.
* **C5-R06 (Expansión del Golden Corpus Canónico):** Ampliar el conjunto de documentos de prueba desde los 5 actuales (`calibration_v1`) hasta el objetivo de 20 a 30 documentos científicos de alta varianza estipulado por la Fase 17_BIS.
* **C5-R07 (Creación del Archivo de Configuración `pyproject.toml`):** Crear `pyproject.toml` en la raíz del repositorio, definiendo la configuración oficial de `pytest` (rutas de descubrimiento, opciones por defecto `-v --tb=short`, reglas de filtrado de advertencias) y perfiles de cobertura de código.
* **C5-R08 (Implementación de Workflow en GitHub Actions - P0):** Crear `.github/workflows/ci.yml` para ejecutar automáticamente la suite completa de pruebas unitarias, de integración, contratos de arquitectura (`test_architecture_contract.py`) y verificaciones de snapshots ante cada evento `push` y `pull_request` a las ramas principales.
* **C5-R09 (Protección de Ramas vía Required Status Checks - P0):** Configurar el workflow de CI en el repositorio remoto como un estado requerido (*Required Status Check*), bloqueando técnicamente la fusión (*merge*) de cualquier Pull Request si alguna aserción de regresión topológica o de snapshot falla.
* **C5-R10 (Gate de Determinismo Criptográfico):** Incluir en la canalización de CI un paso de verificación de determinismo: ejecutar dos pasadas consecutivas de empaquetado sobre el mismo dataset y certificar que la firma hash SHA-256 del resultado sea idéntica ($100\%$ determinismo e idempotencia).

---

## 6. ARQUITECTURA INTEGRADA OBJETIVO DE CI/CD Y REGRESIÓN (FASE 17_BIS)

El modelo de control automatizado que gobernará la protección de fusiones en la Fase 17_BIS queda fijado en el siguiente esquema:

```text
                               ┌─────────────────────────┐
                               │     Pull Request /      │
                               │      Push Event         │
                               └────────────┬────────────┘
                                            │
                                            ▼
                               ┌─────────────────────────┐
                               │     GitHub Actions      │
                               │  (.github/workflows)    │
                               └────────────┬────────────┘
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               │                            │                            │
               ▼                            ▼                            ▼
  ┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
  │      Unit & Smoke       │  │   Regression Snapshots  │  │  Golden Ground Truth    │
  │     (pytest suite)      │  │ (test_chunker_snapshot) │  │  (test_golden_parser)   │
  └────────────┬────────────┘  └────────────┬────────────┘  └────────────┬────────────┘
               │                            │                            │
               └────────────────────────────┼────────────────────────────┘
                                            │
                                            ▼
                               ┌─────────────────────────┐
                               │  Architecture Contract  │
                               │(test_architecture_contr)│
                               └────────────┬────────────┘
                                            │
                             ┌──────────────┴──────────────┐
                             │                             │
                       (All Passed)                   (Any Failed)
                             │                             │
                             ▼                             ▼
                ┌─────────────────────────┐   ┌─────────────────────────┐
                │   Status Check: GREEN   │   │   Status Check: RED     │
                │     (Merge Allowed)     │   │    (Merge Blocked)      │
                └─────────────────────────┘   └─────────────────────────┘
```

---

## 7. EVALUACIÓN DE CONFIABILIDAD Y DECLARACIÓN DE CIERRE

### 7.1 DIAGNÓSTICO DE CONFIABILIDAD REAL
1. **Infraestructura Conceptual de Regresión:** **BUENA BASE CONSTRUCTIVA.**
   Existe una clara intención de arquitectura para proteger el sistema mediante snapshots, inspección de sintaxis LaTeX y un Bounded Context formal para el Ground Truth.
2. **Implementación de Tests de Snapshot Existentes:** **DEFECTUOSA / INESTABLE.**
   `test_chunker_snapshot.py` autogenera baselines en silencio y `test_golden_parser.py` contiene un vicio tautológico ($A == A$) que omite las aserciones reales si la fixture falta.
3. **Mecanismo de Enforcement y Bloqueo en CI:** **INEXISTENTE.**
   Dada la ausencia de `pyproject.toml` y de flujos de GitHub Actions, el repositorio carece del mecanismo necesario para convertir las pruebas en una puerta de enlace (*gate*) que impida regresiones en el código en producción.

---

### 7.2 DECISIÓN FINAL DEL SUB-HITO 0.4.4-C5

The audit for **Block C5 (Snapshots + CI Gates)** is hereby declared **CLOSED**.

```text
====================================================================================
                  ESTADO DE AUDITORÍA: SUB-HITO 0.4.4-C5
====================================================================================
  Audit Status             | CLOSED (Auditoría Finalizada)
  Code Remediation         | DEFERRED (Diferido a Hito 0.5)
  Production Certification | NOT GRANTED (Requiere implementación de CI Workflows)
  Remediation Backlog      | OPEN (Reglas C5-R01 a C5-R10 Registradas)
====================================================================================
```

**Bitácora de Gobernanza:**
> *"Se da por concluida la auditoría del Bloque C5. Se constata la presencia de una base conceptual valiosa para pruebas de regresión, pero se identifican fallas críticas en los tests de snapshots (autogeneración de oráculos y tautologías de comparación) y una ausencia total de canalizaciones de CI automatizadas (.github/workflows/) que bloqueen el merge ante fallos. No se realizaron cambios en código durante C5. Los hallazgos se trasladan al Hito 0.5 como Backlog de Remediación Obligatorio, priorizando la creación de los workflows de CI y el saneamiento de las pruebas de regresión antes de proceder al congelamiento de la baseline científica."*



# HITO_0.4.4_D_E_COVERAGE_MATRIX_AND_PRODUCTION_SCOPING_AUDIT.md
## Matriz de Cobertura Arquitectónica, Solapamiento Topológico y Re-Scoping del Pipeline de Producción — Reporte Consolidado 

* **Estado:** AUDIT SCOPE EXPANDED / HITO 0.4 REMAINS OPEN
* **Fecha de Emisión:** 2026-07-28
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.4 (Sub-hitos 0.4.4-D y 0.4.4-E)
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Reconciliación entre la superficie de evaluación topológica (auditada en C1-C5) y el pipeline real de producción (evidenciado en el `PROJECT_TREE`). Cero mutaciones en código. Bloqueo explícito del pase al Hito 0.5 hasta completar la auditoría de la canalización de *runtime*.

---

## 1. EL HALLAZGO EPISTEMOLÓGICO: LA ILUSIÓN DEL BENCHMARK

La consolidación de los bloques C1 a C5 nos ha llevado a un descubrimiento arquitectónico de primer nivel: **hemos auditado exhaustivamente el arnés de evaluación (*evaluation harness*), pero aún no hemos auditado el pipeline de producción.**

Existe el riesgo crítico de asumir que:
`El Benchmark funciona` $\rightarrow$ `El Parser se evalúa bien` $\rightarrow$ `El Pipeline real es robusto`. 

Esta deducción es **falsa**. El análisis del árbol de proyecto (`PROJECT_TREE.txt`) demuestra que la canalización real de producción involucra una maquinaria transaccional masiva que no es tocada por el benchmark topológico. 

Se deben separar estrictamente tres preguntas arquitectónicas:
1. **Benchmark (`tools/evaluation/`):** *"¿Qué extractor (Docling, PyMuPDF, Marker) reconstruye con mayor precisión la topología del Ground Truth?"* (Evaluación científica competitiva exógena).
2. **Regression (`tests/integration/`, CI Gates):** *"¿El componente que elegimos alteró su comportamiento contractual respecto al oráculo congelado?"* (Protección de línea base y CI).
3. **Pipeline Real de Producción (`core/pipeline/`, `apps/daemons/`):** *"¿El sistema end-to-end realmente invoca esos componentes, conserva las invariantes entre capas, maneja la concurrencia, enruta a los LLMs, ejecuta el auto-healing, gestiona el FSM y persiste transaccionalmente?"* (Runtime).

---

## 2. SOLAPAMIENTO: BENCHMARK VS. REGRESSION (SUB-HITO 0.4.4-E)

Se auditaron los componentes `StructuralTopologyMetric` (Benchmark) y `ASTFingerprintPolicy` (Regression).
* **Diagnóstico:** **NO HAY DUPLICACIÓN**. Aunque ambos consumen el AST y lo comparan contra un oráculo, sus responsabilidades son ortogonales.
  * El **Benchmark** utiliza `ZhangShashaEngine` y `apted` para calcular la Distancia de Edición de Árboles (TED) y asignar un *score* continuo de calidad estructural entre candidatos heterogéneos.
  * La **Regresión** utiliza la huella digital semántica (`ASTFingerprintPolicy`) para detectar mutaciones binarias (Pasa/Falla) en el comportamiento de un único componente en el tiempo.
* **Conclusión:** Ambos subsistemas son complementarios y necesarios para la Fase 17 y 17_BIS.

---

## 3. MATRIZ DE COBERTURA ARQUITECTÓNICA REAL (SUB-HITO 0.4.4-D)

La siguiente matriz corrige la falsa sensación de cobertura al incorporar el **Pipeline Real** como dimensión de análisis. Queda en evidencia la enorme superficie productiva que aún no ha sido escrutada:

| Área del Sistema | Cobertura de Pytest | Cobertura de Benchmark | Cobertura de Regresión | Cobertura en Pipeline Real | Estado de Auditoría |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Invariantes de Dominio** | ✓ | — | — | **?** | 🟡 Parcialmente auditado |
| **AST V2 / Modelos** | ✓ | ✓ | Parcial | **?** | 🟡 Pendiente integración |
| **Extraction Providers** | ✓ | ✓ | ✓ | **?** | 🔴 Pendiente de auditoría |
| **Layout & Document Profile**| ✓ | Parcial | Pendiente | **?** | 🔴 Pendiente de auditoría |
| **Normalización** | ✓ | — | — | **?** | 🔴 Pendiente de auditoría |
| **Segmenter V2 / Chunking** | ✓ | Indirecto | Parcial | **?** | 🔴 Pendiente de auditoría |
| **Routing / FinOps** | ✓ (Tests) | — | — | **?** | 🔴 Pendiente de auditoría |
| **Validación Pre / Post-LLM**| ✓ (Tests) | — | — | **?** | 🔴 Pendiente de auditoría |
| **Auto-Healing** | ✓ (Tests) | — | — | **?** | 🔴 Pendiente de auditoría |
| **Prompting / LLM Dispatch** | ✓ (Tests) | — | — | **?** | 🔴 Pendiente de auditoría |
| **Pipeline Orchestration** | ✓ (Tests) | — | — | **?** | 🔴 Pendiente de auditoría |
| **CQRS / FSM / Recovery** | ✓ (Tests) | — | — | **?** | 🔴 Pendiente de auditoría |
| **Compiler & Assembler** | ✓ (Tests) | — | Parcial | **?** | 🟡 Parcial |
| **Serialization** | Indirecto | Parcial | Parcial | **?** | 🟡 Parcial |
| **Telemetry / Metrics** | ✓ (Tests) | ✓ | — | **?** | 🔴 Pendiente de auditoría |
| **E2E Reconciliation** | — | — | Parcial | **?** | 🔴 Pendiente de auditoría |

---

## 4. LA SEGUNDA MITAD: EL PIPELINE DE PRODUCCIÓN

El análisis del `PROJECT_TREE.txt` revela que la Fase 17 no puede cerrarse sin auditar las siguientes 8 familias de producción pura. El hecho de que el `GeminiBenchmarkRunner` funcionara no significa que el `LLMWorkerDaemon` productivo respete las reglas.

### Superficie Pendiente de Producción:
1. **Extraction & Layout Físico:** `core/extraction/ocr_providers/*`, `infra/adapters/pdf_parser.py`, `core/layout/*`. (¿Es `DocumentLayout` realmente el contrato físico respetado?)
2. **AST V2 $\rightarrow$ Normalization $\rightarrow$ Segmentation:** `core/normalization/*`, `core/segmenter/*`. (¿Qué ocurre con la normalización HTML, Latex Sanitizer, y los Fixers antes del chunking?)
3. **Prompting $\rightarrow$ Routing $\rightarrow$ LLM Dispatcher:** `core/prompting/*`, `apps/llm_workers/*`, `core/finops/*`. (¿Cómo se enrutan los constraints y se limitan los rate limits en Groq/Gemini?)
4. **Validation & Healing Post-Translation:** `core/validation/` (Semantic, Structural, Perimeter), `core/healing/*`. (¿Qué sucede cuando el LLM alucina un bloque de Markdown? ¿Entra en bucle infinito?)
5. **Orquestación de Pipeline Real:** `core/pipeline/*` (`TranslationPipeline`, `orchestrator.py`).
6. **Execution, CQRS & FSM:** `core/execution/*`, `infra/db/*`. (El motor transaccional: ¿Cómo transiciona un `TranslationJob`? ¿Qué pasa en el `ControlPlaneRepository`?)
7. **Runtime & Recovery:** `runtime/*` (`reconciliation.py`, `recovery.py`, `sweeper.py`), `apps/daemons/*`. (¿Cómo se recuperan las tareas zombie?)
8. **Compiler & Telemetry:** `core/telemetry/*`, `core/metrics/*`. (Métricas de negocio, SLOs, densidad PDF).

---

## 5. HOJA DE RUTA OBLIGATORIA (SUB-HITOS 0.4.4-P1 A P9)

Para declarar el **Hito 0.4 COMPLETADO** y poder consolidar las decisiones en el Hito 0.5, se debe ejecutar una segunda campaña de auditoría focalizada exclusivamente en la arquitectura de *Runtime/Producción*.

Se estructurará en los siguientes 9 bloques lógicos:

* **0.4.4-P1 — Extraction + Physical Layout:** (`core/extraction/`, `infra/adapters/pdf_parser.py`, `core/layout/`).
* **0.4.4-P2 — AST V2 + Normalization:** (`core/ast/`, `core/normalization/`).
* **0.4.4-P3 — Segmenter + Chunker + Context Enrichment:** (`core/segmenter/`, `core/chunking/`, `core/context/`).
* **0.4.4-P4 — Validation + Healing:** (`core/validation/`, `core/healing/`).
* **0.4.4-P5 — Prompting + Routing + Dispatcher + FinOps:** (`core/prompting/`, `apps/llm_workers/`, `core/routing/`, `core/finops/`).
* **0.4.4-P6 — Pipeline Orchestrator + Application Composition:** (`core/pipeline/`, `apps/bootstrap/`, `apps/cli/`).
* **0.4.4-P7 — Execution State (FSM) + CQRS + Persistence + Recovery:** (`core/execution/`, `infra/db/`, `runtime/`, `apps/daemons/`).
* **0.4.4-P8 — Compiler + Output Artifact + Telemetry:** (`core/compiler/`, `core/telemetry/`, `core/metrics/`).
* **0.4.4-P9 — End-to-End Architecture Reconciliation:** (Revisión de integración total).

---

## 6. VEREDICTO FINAL Y DECLARACIÓN DE ESTADO

1. **Sobre la Planificación Original:** **SÍ, ESTAMOS DENTRO DE LO PLANEADO.** Los hallazgos C1-C5 son totalmente válidos y destaparon la deuda técnica exacta de la superficie de Evaluación/Ground Truth que la Fase 17 requiere.
2. **Sobre el Cierre del Hito 0.4:** **SE DECLARA FORMALMENTE ABIERTO.** Sería un error metodológico grave asumir que validar el Benchmark equivale a validar el Traductor. 
3. **Sobre el Avance al Hito 0.5:** **BLOQUEADO.** No se procederá a consolidar decisiones ni a redactar el ADR final (`FROZEN`) hasta que el pipeline real de producción (P1 a P9) haya sido escrutado bajo el mismo estándar forense.

```text
====================================================================================
                  ESTADO DE AUDITORÍA: SUB-HITOS 0.4.4 (GLOBAL)
====================================================================================
  Test Suite Audit (Unit/Integration)      | CLOSED (Auditoría Finalizada)
  Benchmark & Regression Audit (C1-C5)     | CLOSED (Backlog de Remediación Abierto)
  Coverage & Overlap Matrix (D-E)          | CLOSED (Matriz Expandida a Producción)
  Production Pipeline Audit (P1-P9)        | OPEN (Pendiente de Ejecución)
  ----------------------------------------------------------------------------------
  HITO 0.4 STATUS                          | OPEN
  HITO 0.5 STATUS                          | BLOCKED
====================================================================================