# HITO_PPPR.0.6_G5_ENSAMBLADO_Y_PDF_SALIDA.md

**Estado:** IN_PROGRESS v1.0.1  
**Fecha de emisión:** 2026-11-19  
**Congelamiento:** N/A  
**Tipo:** Forensic Flow Audit — G5, representación TeX, compilación y salida PDF  
**Iniciativa:** PPPR, Fase 0 de auditoría documental transversal; no altera fases del roadmap.  
**Baseline productivo:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42` (no modificar).  
**Baseline de gobernanza:** `pdf-pdf-product-readiness@30175a0fbdd2774bc1a4ef00d83e57c96a16fa7d` (PPPR.0.1–0.5 FROZEN).  
**Mandato:** inspeccionar la ruta seleccionada G3→G5→PDF: contexto/AST/proyecciones, validaciones y degradación, jerarquía de nodos, ecuaciones/TeX, tablas/código, imágenes/activos, perfil y geometría, Tectonic, lease/FSM/FS, publicación, recuperación y garantías verificables. Separar integridad operativa de fidelidad científica.  
**Metodología superior:** `docs/architecture/1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` v1.3.0 FROZEN; `docs/architecture/1.2_METH_FOR_FORENSIC_HITOs.md` v1.2.0 FROZEN; `PROJECT_SCOPE.md` y `ENGINEERING_PRINCIPLES.md`. D-1/D-2, Atlas de ruta única y PPPR.0.1–0.5 FROZEN.  
**Normativa primaria para reconciliar:** NADR-F17BIS-06 (§5.2–5.3, TeX y servicio canónico); NADR-F17BIS-09 (§5.1–5.2, FSM, aislamiento y veracidad del compilador); F18-03/04 (autoridad, recuperación) y contratos B02.2/B02.4/B02.5/G5.2.  
**Carácter de la evidencia:** código de repositorio y pruebas versionadas leídas, **NOT_RUN**. No se ejecutaron Tectonic, Docker, APIs, SQLite, corpus ni PDF científico. No se afirma `PRODUCT_READINESS=PASS`.

### Changelog

| Versión | Fecha | Alcance |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-11-19 | Apertura desde merge #70, 24 E-IDs preliminares, 9 hipótesis de contraste y ninguna promoción automática de defectos históricos P6; auditoría read-only G5/compilación/artefactos. |
| 1.0.1-IN_PROGRESS | 2026-11-19 | Segunda pasada: 34 E-IDs, 3 fichas P1 locales y 3 GAP OPEN sobre CODE/TABLE literal, semántica HEADING y macros TeX legítimas fuera de math. H-0.6-A/B confirmadas, C/D/E/F/G/H/I delimitadas; antecedente GAP-0.2-02 y P6 reconciliados. Testigos NOT_RUN, sin FROZEN ni implementación. |

## 1. RESUMEN EJECUTIVO

El G5 soportado recibe un documento `READY_FOR_ASSEMBLY` desde el flujo CLI→OCR→G3, o es reclamado por el daemon ensamblador. Ambas composiciones utilizan `AssemblerWorkerDaemon._process_assembly_task`, `AssemblyLeaseRepository`, `CQRSAssemblyContextResolver`, `DocumentAssembler`, `CompilationService`, `HostTectonicRunner` y publicación fenced. La ruta actual **no** reproduce el bypass histórico del servicio, el falso DockerRunner ni la escritura principal del compilador en `os.getcwd()`.

**Garantías observables, todavía limitadas:** validación de secuencia y unicidad antes de OMIT, materialización de proyecciones por generación/versión, fallback con comprobación SHA cuando procede, perfil SQLite durable, bundle de imágenes por digest, escapado de prosa separado de spans matemáticos, ejecución Tectonic aislada por intento y exclusión de publish por owner/lease caducado. `%PDF-` + FSM `COMPLETED` constituyen una comprobación **operativa mínima**, nunca certificación de layout, fórmulas o calidad lingüística `en→es`.

**Defectos locales P1 confirmados por flujo estático:** (a) CODE/TABLE entran como TeX crudo aunque son contenido literal, **GAP-0.6-01**; (b) `HeadingPayload.heading_level` y `ASTNode.depth` se pierden al crear RenderUnit y HEADING se renderiza como PARAGRAPH, **GAP-0.6-02**; (c) macros TeX legítimas de texto fuera de spans math son escapadas indiscriminadamente, **GAP-0.6-03**. Ninguno constituye una incidencia de Tectonic real demostrada. Geometría, recuperación física, DEGRADED y calidad científica permanecen acotadas, no convertidas en GAP por intuición.

**Veredicto de segunda pasada:** **IN_PROGRESS v1.0.1**: 34 E-IDs, 3 P1 locales OPEN y siete evidencias nuevas P2. El mandato estático G5 aún requiere reconciliar más profundamente fallback, pruebas físicas y no-regresión antes de §8.1–8.2. Ni `FROZEN` ni `PRODUCT_READINESS=PASS`.

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

- **Observed:** implementación textual de `main@1d21cfe` y contratos de tests versionados. Un test leído **no** es un test ejecutado; un PDF con magic header **no** es evidencia de preservación visual o científica.
- **Required:** PROJECT_SCOPE exige integridad matemática/técnica y rastreabilidad topológica, con layout de salida; NADR-F17BIS-06 exige preservación de TeX legítimo y paso por `CompilationService`; NADR-F17BIS-09 exige aislar compilación, no sintetizar transiciones y nombrar el ejecutor con veracidad; F18 protege autoridad/recuperación.
- **Decision:** D-1/D-2 define CLI→OCR→G3 (`runtime/engine.py`)→G5 (`apps/compiler/__main__.py`). No se introduce otro ensamblador, renderer, OCR o editor visual por defecto.
- **NO VERIFICABLE en este corte:** fidelidad tipográfica, equivalencia visual PDF original/objetivo, exactitud matemática real, protección ante fallos físicos de almacenamiento, fondos privados de corpus GT, font coverage, recuperación SIGKILL, medidas de costo y calidad idiomática `en→es`.
- **No se modificaron:** producción, tests, estados SQLite, output físico, corpora/certificación, configuración de proveedor ni otros HITOs FROZEN.

## 3. ALCANCE AUDITADO — INVENTARIO INICIAL

| Frontera | Código/artefacto observado | Estado |
|---|---|---|
| Entrada/reanudación G5 desde CLI | `apps/cli/pdf_product.py::_run_g5/run_admitted_pdf/_verify_published_pdf` | **AUDITADO** (E-001/002/024) |
| Daemon assembler y fases FSM | `apps/compiler/__main__.py::AssemblerWorkerDaemon` | **AUDITADO** (E-003/004/020) |
| Lease, fencing y crash | `infra/db/assembly_recovery.py::AssemblyLeaseRepository` | **AUDITADO focal** (E-005/018/019) |
| AST/continuidad, OMIT, proyecciones | `core/compiler/context_resolver.py::CQRSAssemblyContextResolver` | **AUDITADO** (E-006) |
| Aceptación/degradación/fallback | `core/compiler/assembler.py`, `core/compiler/service.py`, `infra/db/document_repository.py` | **AUDITADO focal** (E-007/008) |
| Perfil y geometría | `infra/db/profile_store.py`, `apps/compiler/__main__.py::RenderGeometryAdapter` | **AUDITADO focal** (E-009/010) |
| Render por tipo, TeX y estructura | `core/compiler/rendering/{context,implementations,mapper,models}.py`, `apps/compiler/tex_builder.py`; `core/ast/{builder,models,strategy}.py` | **AUDITADO focal** (E-011…015 y E-025…027/033), tres incongruencias P1 |
| Imágenes y materialización física | `core/compiler/rendering/image_assets.py`, `apps/compiler/tectonic_runner.py` | **AUDITADO focal** (E-016/017) |
| Testigos offline | B03, B02.2/B02.4/B02.5, G3/B4.4, G5 lease/worker, TeX renderer/Tectonic | **LEÍDOS · NOT_RUN** (E-021…023) |
| Historia P6 | HITO F17BIS P6 y NADR-F17BIS-06/-09 | **RECONCILIACIÓN POR DELTA**; no reabrir automáticamente P6-H01…04 |
| Calidad real PDF en corpus, GT, producto y despliegue | PPPR.0.8/0.9 y PPPR.0.7 según contrato | **REFERENCIADO / NO VERIFICABLE** |

## 4. FUENTES DE EVIDENCIA

**Código activo fijo:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`: `apps/cli/pdf_product.py`; `apps/compiler/{__main__,tectonic_runner,tex_builder}.py`; `infra/db/{assembly_recovery,profile_store,materialized_repo,document_repository}.py`; `core/ast/{builder,models,strategy,enums}.py`; `core/normalization/explicit_math.py`; `infra/extraction/providers/{pymupdf_provider,pymupdf_math_visual}.py`; `core/compiler/{assembly_context,context_resolver,assembler,service}.py`; `core/compiler/rendering/{mapper,models,context,implementations,image_assets}.py`.

**Contratos:** `docs/architecture/adr/phase-17-bis/NADR/NADR_06_Token_Estimation_Compilation_Governance.md` (§5.2 R5–R8 y §5.3 R9–R12); `docs/architecture/adr/phase-17-bis/NADR/NADR_09_FSM_Event_Integrity_Compiler .md` (§5.2 R6–R9); F18 NADR-03/-04; `docs/architecture/adr/phase-17-bis/00-foundation/HITO_0.4.5_P6_ASSEMBLY_COMPILER_AUDIT.md` **histórico**; Atlas operativo; PPPR.0.1–0.5 FROZEN.

**Testigos versionados (NO RUN):** `tests/integration/{test_b03_foreground_pdf_product,test_g3_b4_4_profile_projection_assembly,test_g5_assembler_lease_recovery,test_g5_assembler_worker_integration,test_b024_g3_g5_math_roundtrip,test_b025_math_visual_preservation}.py`; `tests/unit/{test_assembler,test_b022_image_rendering,test_text_render_strategy,test_tectonic_runner}.py`. Los tests de G5 usan mayormente DB temporales, fakes para renderer/runner o insumos sintéticos; **no** acreditan corrida real con proveedor o equivalencia de papers.

## 5. MAPA DE FLUJO G5 SELECCIONADO

```text
CLI run_admitted_pdf
   G3 → FSM READY_FOR_ASSEMBLY
   _run_g5 → AssemblerWorkerDaemon._process_assembly_task
      [también existe worker daemon que toma READY_FOR_ASSEMBLY por FSM]
      AssemblyLeaseRepository.claim:
        queue.db + fsm_db ATTACH, lease owner/execution_id, FSM→ASSEMBLING
      Heartbeat SQLite desde conexión de otro hilo (cada 30 s)
      CQRSAssemblyContextResolver.resolve:
        ASTRegistry → unicidad/continuidad → OMIT fuera
        MaterializedPlaneRepository → proyecciones CURRENT verificadas
      CompilationService.compile_document_with_assets:
        DocumentAssembler (tolerancia máx 5 %, fallback condicional)
        SQLiteProfileStore(documents.db) → perfil verificado
        payloads por proyección o fallback SHA en documents.db
        RenderUnitMapper → RenderContext → TexBuilder
        spans math, tabla/código raw, imagen por asset digest
      AssemblyLeaseRepository.advance:
        ASSEMBLING → READY_FOR_COMPILATION → COMPILING
      HostTectonicRunner:
        TemporaryDirectory, assets PNG hash-verified, --untrusted,
        timeout 120s; copia a output/.assembly_<uuid>.pdf
      AssemblyLeaseRepository.publish:
        validar header/paths; lock SQLite; CAS lease+FSM+queue
        os.replace(artifacto privado, translated_<doc_id>.pdf)
        COMMIT queue + FSM adjunta (sin atomicidad con filesystem)
      CLI verifica FSM COMPLETED, archivo regular y %PDF- (operacional)
```

**Lectura estricta:** la línea feliz no prueba eficacia de render visual; un crash entre rename y commit puede dejar el PDF en filesystem con FSM no COMPLETED, situación de recuperación regenerable documentada, no commit distribuido. Los checks de header/estado no comparan páginas, fórmulas, figuras ni layout.

## 10. REGISTRO DE EVIDENCIA FORENSE — SEGUNDA PASADA (NO FROZEN)

| E-ID | Sev. inicial | Observed (archivo::símbolo) | Required/Decision/límite | Disposición |
|---|---|---|---|---|
| **E-0.6-001** | P2 | `pdf_product.py::run_admitted_pdf` ejecuta solo la rama G5 si FSM READY_FOR_ASSEMBLY; para COMPLETED verifica PDF sin reconstruir. | Ruta única/estado operacional D-1/D-2; no implica calidad visual. | OBSERVADO |
| **E-0.6-002** | P2 | `pdf_product.py::preflight_product_run` exige Tectonic y tres bases; `_verify_published_pdf` requiere regular, tamaño mínimo y prefijo `%PDF-`. | Precondición y predicado de éxito **operativos**, no validador integral PDF ni benchmark. | OBSERVADO |
| **E-0.6-003** | P2 | `pdf_product.py::_run_g5` y `apps/compiler/__main__.py::main` inyectan `CompilationService`, `DocumentAssembler`, `SQLiteProfileStore`, `CQRSAssemblyContextResolver`, `HostTectonicRunner`. | NADR-F17BIS-06 §5.3 R9/10; bypass ad-hoc histórico P6-H01 **no vigente** en ruta seleccionada. | RECONCILIACIÓN |
| **E-0.6-004** | P2 | `AssemblerWorkerDaemon::_process_assembly_task` reclama tarea y hace heartbeat de conexión dedicada; compila a `.assembly_<uuid>.pdf` y usa `leases.publish`. | Contrato G5/2 de autoridad y artefacto privado; no prueba compilar documento científico real. | OBSERVADO |
| **E-0.6-005** | P2 | `AssemblyLeaseRepository::claim/advance/publish` liga `owner/execution_id/TTL` a queue.db y FSM adjunta, con CAS antes de publish. | F18 autoridad/attempt; no asumir cancelación física de Tectonic. | OBSERVADO |
| **E-0.6-006** | P2 | `CQRSAssemblyContextResolver::resolve` valida AST completo, unicidad y continuidad `sequence_id` antes de excluir OMIT; usa `projection_version=1` y generación AST. | Contrato NADR-06 de secuencia íntegra y no falsos gaps tras OMIT. | OBSERVADO |
| **E-0.6-007** | P2 | `DocumentAssembler::assemble` acepta completo o DEGRADED si faltan hasta 5 % de proyecciones con `allow_fallback=True`, rechaza más. | Política de aceptación explícita; no equiparar DEGRADED a fidelidad ni disponibilidad de payload. | OBSERVADO |
| **E-0.6-008** | P2 | `CompilationService::compile_document_with_assets` busca proyección por nodo o `get_verified_payload` con `chunk_id/payload_sha256` y falla ante falta/drift. | Fallback criptográficamente verificado cuando hay datos; calidad científica no evaluada. | OBSERVADO |
| **E-0.6-009** | P2 | `SQLiteProfileStore::save/get` guarda layout/tipo con SHA por documento en `documents.db` y rechaza tampering/replay conflict. | Perfil durable de OCR→G5, no fuente de geometría física exacta. | OBSERVADO |
| **E-0.6-010** | P2 | `RenderGeometryAdapter::extract` normaliza `bboxes` con fallback **612×792 pt**; hay `page_number=metadata.pages[0]`. | Geometría real por página no garantizada; relacionar con GAP-0.2-02 sin duplicar por homonimia. | H-0.6-D |
| **E-0.6-011** | P2 | `RenderContextFactory::create` elige article A4 una/dos columnas usando perfil; registra estrategias por `ContentNodeType`. | No reconstruye por sí mismo el layout físico de la fuente. | OBSERVADO |
| **E-0.6-012** | P2 | `TextRenderStrategy::render` escapa prosa y conserva spans explícitos `$...$ / \(...\)`; `InlineMathProtector` comparte delimitadores en testigos B02.4. | NADR-F17BIS-06 §5.2 R5–R8: proteger TeX legítimo, no certificar corrección algebraica. | TESTIGO/OBSERVADO |
| **E-0.6-013** | P2 | `PassthroughRenderStrategy::render` retorna `unit.content` crudo para CODE, TABLE_SIMPLE/COMPLEX, DISPLAY/INLINE_EQUATION y COMPOSITE_BLOCK. | Comprobar que literal code/table no se ejecuta o malinterpreta como comandos TeX; sin contrajemplo aún en la ruta seleccionada. | H-0.6-A/C |
| **E-0.6-014** | P2 | `RenderContextFactory` asigna **HEADING y PARAGRAPH a la misma `TextRenderStrategy`**; `TexBuilder` concatena renderizados sin indicación directa de heading level. | Riesgo de pérdida de jerarquía visual; verificar downstream y contrato semántico antes de GAP. | H-0.6-B |
| **E-0.6-015** | P2 | `AdaptiveFloatStrategy` produce `figure` o `figure*` por ancho relativo y perfil de columnas; `RenderUnitMapper` adjunta geometry/asset. | Preserva referencia a figura; no acredita ubicación/pie de figura ni layout exacto. | OBSERVADO |
| **E-0.6-016** | P2 | `canonical_image_name/stage_image_assets` exigen `data/assets/<sha256>.png`, firma PNG, hash de bytes y rutas sin symlink; los recursos solo se copian al cwd efímero. | Preservación visual por asset con integridad; no prueba exactitud semántica del dibujo. | OBSERVADO |
| **E-0.6-017** | P2 | `HostTectonicRunner::compile` usa `TemporaryDirectory`, `tectonic --untrusted doc.tex`, timeout 120 s, y copia al nombre privado autorizado por caller. | NADR-F17BIS-09 §5.2 R6–R9; no hay aislamiento de contenedor prometido ni prueba de compilación física. | OBSERVADO |
| **E-0.6-018** | P2 | `AssemblyLeaseRepository::publish` ejecuta `os.replace` bajo `BEGIN IMMEDIATE` tras CAS de FSM/queue, pero **antes** de COMMIT de SQLite. | Publicación fenced en operación, **no** atomicidad FS+SQLite ni power-loss PASS. | H-0.6-E |
| **E-0.6-019** | P2 | `AssemblyLeaseRepository::recover_expired` reencola con epoch de reconciler, CAS, max_retries y FSM no terminal; sin reuso del artefacto físico parcial como estado confirmado. | Contrato G5/2 de recuperación reproducible; tests G5 NOT_RUN. | OBSERVADO |
| **E-0.6-020** | P2 | `AssemblerWorkerDaemon` usa `fail_authorized` tras error y limpia solo el PDF privado de su intento; no borra final de otro owner. | Fencing de fracaso y cleanup limitado; no prometer recuperación de errores estructurales automáticamente. | OBSERVADO |
| **E-0.6-021** | P2 | `test_g5_assembler_lease_recovery` y `test_g5_assembler_worker_integration` contienen escenarios de dueño doble, expiración, requeue, rollback tras promoción, ausencia de proyección. | Testigos con SQLite temporal y FakeRunner: **NOT_RUN**, no PDF científico en físico. | TESTIGO |
| **E-0.6-022** | P2 | B03 foreground y G3/B4.4 verifican estados, preflight, perfil SQLite y projection digest; usan rutas/fakes locales. | Conexión operacional versionada, no evidencia de calidad física o de corpus. | TESTIGO |
| **E-0.6-023** | P2 | B02.4 preserva bytes de spans de math; B02.5 genera fórmula visual como IMAGE/PRESERVE, pero señala que no evalúa semántica matemática/layout. | Separar preservación sintáctica/visual de fidelidad científica. | TESTIGO |
| **E-0.6-024** | P2 | `_verify_published_pdf` valida solo cabecera binaria PDF y FSM COMPLETED; `PDFProductResult.scientific_status` es NOT_CERTIFIED. | No afirmar que PDF compilable/documento completado sea ciencia o presentación equivalente. | LÍMITE EXPLÍCITO |
| **E-0.6-025** | **P1** | `core/ast/builder.py::FlatASTBuilder._TYPE_MAPPING` admite CODE/TABLE; `core/ast/strategy.py` los enruta; `RenderContextFactory` asigna CODE/TABLE_SIMPLE/TABLE_COMPLEX a `PassthroughRenderStrategy` que retorna contenido crudo; `TexBuilder.build` lo concatena directamente en el documento TeX. | `PROJECT_SCOPE.md` §§2/4 exige supervivencia intacta de código e invariantes; NADR-F17BIS-06 §5.2 R5–R7 diferencia *texto literal* y TeX legítimo. Un payload literal con `_`, `&`, `%` o `\\input{...}` es interpretado por TeX y puede fallar o mutar la representación. Caso causal condicionado a recibir el tipo, **no ejecutado**. | **GAP-0.6-01 OPEN** |
| **E-0.6-026** | **P1** | `HeadingPayload.heading_level` admite H1/H2/H3 y `ASTNode.depth` registra jerarquía; `FlatASTBuilder` la transporta. `DefaultRenderUnitMapper` pasa solo node_id, tipo, texto, geometría y activo; `RenderContextFactory` usa `TextRenderStrategy` idéntica para HEADING/PARAGRAPH y `TexBuilder` nunca emite `\\section`/`\\subsection` por nivel. | `PROJECT_SCOPE.md` §2 exige alineación de jerarquías estéticas y §4 topología rastreable; `ENGINEERING_PRINCIPLES.md` §§II/IV exige linaje de depth/parent. El nivel no llega al TeX: dos headings con textos idénticos H1/H2 son visualmente indistinguibles salvo comentarios no tipográficos. | **GAP-0.6-02 OPEN** |
| **E-0.6-027** | **P1** | `TextRenderStrategy.render` solo preserva segmentos detectados por `find_explicit_math_spans`; fuera de ellos llama `LatexEscaper.escape`, que cambia `\\`, `{` y `}`. Una macro legítima como `\\textbf{Resultado}` queda convertida a texto literal en lugar de marcar negrita. | NADR-F17BIS-06 §5.2 **R5/R6/R7/R8** exige preservar TeX legítimo y distinguir contexto, incluidos comandos; testigo unitario cubre math/prosa pero no este macro textual. Es incumplimiento del subconjunto TeX legítimo, sin claim de que todo PDF contenga la macro. | **GAP-0.6-03 OPEN** |
| **E-0.6-028** | P2 | `RenderGeometryAdapter` normaliza anchos con **612 pt**, y `AdaptiveFloatStrategy` usa `relative_width > 0.6` para decidir `figure*` vs `figure` en dos columnas; PyMuPDF conoce el ancho real, pero `NodeMetadata` no lo traslada. | Consecuencia downstream específica del mismo déficit de ancho que **GAP-0.2-02**: figura de 300pt en página 400pt debería resultar 0.75, pero el adapter da 0.49. **No duplicar GAP** hasta decidir si el contrato de layout exige fidelidad exacta; ejemplo estático sin PDF probado. | PROPAGACIÓN DE GAP-0.2-02 |
| **E-0.6-029** | P2 | `core/normalization/explicit_math.py` detecta `$...$`, `$...$`, `\\(...\\)`, `\\[...\\]` y entornos enumerados; falla ante delimitadores desequilibrados, pero no infiere fórmulas de OCR o TeX no explícito. | Falsación parcial de H-0.6-C: protección de spans delimitados no implica reconstruir todas las fórmulas STEM ni cubrir fuentes Unicode. La matemática visual B02.5 es ruta distinta de IMAGE. | H-0.6-C PARCIAL |
| **E-0.6-030** | P2 | `DocumentAssembler` permite `DEGRADED` con hasta 5% de proyecciones ausentes y `allow_fallback`; `CompilationService` usa `get_verified_payload` de `original_chunks` pero solo propaga TeX/activos, no `AssemblyReport.status`. | `AssemblyExecutionContext` aclara que «missing» incluye PASSTHROUGH sin traducción. Queda sin demostrar que se publique una traducción incompleta por la ruta G3 normal; evaluar telemetría y política antes de un GAP de degradación silenciosa. | H-0.6-F ABIERTA |
| **E-0.6-031** | P2 | `AssemblyLeaseRepository.publish` valida artefacto privado, bloquea writer SQLite, actualiza queue/FSM, realiza `os.replace` y recién luego COMMIT; `recover_expired` reencola intento no terminal con CAS y epoch. | F17BIS-09 §5.2 R6/7 y F18 delimitan aislamiento/fencing; `test_g5_assembler_lease_recovery` incluye casos de rollback y promoción completa antes del commit, **NOT_RUN**. No garantizar atomicidad FS+SQL ni recuperación física universal. | H-0.6-E DELIMITADA |
| **E-0.6-032** | P2 | `PyMuPDFProvider.capabilities.has_tables=False`; no afirmar extracción nativa universal de tablas. `FlatASTBuilder._TYPE_MAPPING` acepta tipos `TABLE_SIMPLE/TABLE_COMPLEX/CODE_BLOCK` si el clasificador los produce. | GAP-0.6-01 es un defecto del **consumidor G5 para tipos admitidos**, no una frecuencia acreditada en corpus ni garantía de que cada tabla del PDF sea detectada. | LÍMITE DE ALCANZABILIDAD |
| **E-0.6-033** | P2 | `RenderContextFactory` decide layout solo por `PageLayout.DOUBLE_COLUMN`; `LatexPreambleBuilder` fija A4/11pt y `TexBuilder` no consume geometría para prosa/tablas. El único uso actual de ancho relativo es el float IMAGE. | La reconstrucción física no equivale a copiar cada coordenada; falsación H-0.6-D requiere política explícita de tolerancia, no promesa de pixel-perfect sin corpus. | LAYOUT LIMITADO |
| **E-0.6-034** | P2 | En los testigos `test_text_render_strategy`, `test_b024_g3_g5_math_roundtrip` y `test_b022_image_rendering` se verifican matemáticas delimitadas, prosa e IMAGE; no se ve falsador de CODE/TABLE crudo ni render por `heading_level` en esos archivos. `test_b03_foreground_pdf_product` usa PDF sintético con prefijo PDF. | Contrato parcial en fuentes leídas, **NOT_RUN**; la ausencia de test local no se presenta como fallo ejecutado ni como censo exhaustivo de toda la suite. | TESTIGOS ACOTADOS |

**Severidad de la segunda pasada:** E-0.6-001…024 conservan IDs y P2; E-025/026/027 son **P1 LOCAL** con consumidores y normas cotejados; E-028…034 son P2 de propagación/límite/testigo. Ningún P0 o incidencia comercial/física declarados. Los ejemplos de caracteres TeX y tamaños de página son falsadores estáticos, no PDFs producidos.

### Fichas extendidas P1 (metodología §4.7)

#### E-0.6-025 — CODE/TABLE literal se interpreta como TeX (P1)

- **Archivo/símbolos:** `core/ast/builder.py::FlatASTBuilder._TYPE_MAPPING`; `core/ast/strategy.py::resolve_strategy`; `core/compiler/rendering/context.py::RenderContextFactory.create`; `core/compiler/rendering/implementations.py::PassthroughRenderStrategy.render`; `apps/compiler/tex_builder.py::TexBuilder.build`.
- **Declaración observada:**

```python
# RenderContextFactory
ContentNodeType.TABLE_SIMPLE: passthrough_strategy,
ContentNodeType.TABLE_COMPLEX: passthrough_strategy,
ContentNodeType.CODE: passthrough_strategy,
# PassthroughRenderStrategy
return unit.content or ""
# TexBuilder: después de comentario NODE_ID/TYPE
document.append(rendered_content)
```

- **Observed:** los tipos AST CODE/TABLE están admitidos; el consumidor G5 introduce su contenido directamente en cuerpo TeX sin envoltura literal ni distinción de código/tablas frente a macros TeX. Una línea de código como `int x_y = 1;` contiene `_` significativo para TeX fuera de math; una celda con `%` puede iniciar comentario o `&` tabular fuera de contexto. El resultado de Tectonic y la frecuencia en PDFs reales **no se ejecutaron**. `PyMuPDFProvider.has_tables=False` limita una afirmación de cobertura universal de tablas, pero no invalida la rama de render para un nodo tipado recibido.
- **Required:** `PROJECT_SCOPE.md` §§2/4 exige preservar código y contenido científico sin mutación silenciosa; NADR-F17BIS-06 §5.2 R5–R7 exige escapado según contexto que preserve TeX legítimo y trate el texto literal como tal.
- **Decision:** la ruta G5 es única y pasa por `CompilationService`; no se autoriza reemplazarla ni introducir otra sintaxis de tablas a priori.
- **Consecuencia:** TeX puede interpretar, comentar o rechazar caracteres de código/celdas, en lugar de producir una representación literal fiel. No se atribuye explotación del host ni error físico ocurrido.
- **Severidad:** **P1 LOCAL OPEN → GAP-0.6-01**. Destino: ADR Maestro/Execution Plan, testigo focal sin LLM y sin corpus privado.

#### E-0.6-026 — jerarquía HEADING conservada en AST pero descartada en render (P1)

- **Archivo/símbolos:** `core/ast/models.py::HeadingPayload.heading_level/ASTNode.depth`; `core/ast/builder.py::FlatASTBuilder`; `core/compiler/rendering/mapper.py::DefaultRenderUnitMapper.map_to_unit`; `core/compiler/rendering/context.py::RenderContextFactory.create`; `apps/compiler/tex_builder.py::TexBuilder.build`.
- **Declaración observada:**

```python
# AST:
heading_level: HeadingLevel = HeadingLevel.UNKNOWN
# RenderContextFactory:
ContentNodeType.PARAGRAPH: text_strategy,
ContentNodeType.HEADING: text_strategy,
# DefaultRenderUnitMapper returns RenderUnit(
# node_id, node_type, content, geometry, asset)
```

- **Observed:** el nivel H1/H2/H3 y `depth` del AST existen, pero `RenderUnit` no los porta; HEADING y PARAGRAPH usan el mismo renderizador que devuelve prosa escapada, y `TexBuilder` emite comentarios de depuración con TYPE sin comando de sección ni tratamiento tipográfico del nivel. Un cambio H1↔H2 de igual texto llega a TeX tipográficamente indistinguible. `OMIT` y `sequence_id` siguen validados; no se infiere pérdida de nodos.
- **Required:** `PROJECT_SCOPE.md` §2 (ensamblador de layout para jerarquías estéticas), §4 (completitud topológica), `ENGINEERING_PRINCIPLES.md` §§II/IV (AST plano con depth/parent; propagación de linaje). El requerimiento **no** impone un estilo LaTeX o `\\section` determinado.
- **Decision:** `GAP-0.3-01` ya trata jerarquía **omitida en identidad/hash**, otro consumidor y consecuencia. No se duplica ese GAP: aquí se pierde representación visual en PDF.
- **Consecuencia:** el artefacto de salida no representa los niveles estructurales tipados aunque el AST los conocía; no se cuantificó efecto real de diagramación.
- **Severidad:** **P1 LOCAL OPEN → GAP-0.6-02**. Destino: ADR Maestro/Execution Plan, con verificación de H1/H2/H3 en TeX/PDF sintético.

#### E-0.6-027 — TeX legítimo fuera de math es escapado como prosa (P1)

- **Archivo/símbolos:** `core/normalization/explicit_math.py::find_explicit_math_spans`; `core/compiler/rendering/implementations.py::{TextRenderStrategy.render,LatexEscaper.escape}`.
- **Declaración observada:**

```python
# TextRenderStrategy:
for start, end in find_explicit_math_spans(text):
    result.append(LatexEscaper.escape(text[position:start]))
    result.append(text[start:end])
result.append(LatexEscaper.escape(text[position:]))
# LatexEscaper: "\\" → "\\textbackslash{}", "{" → "\\{", "}" → "\\}"
```

- **Observed:** el parser protege delimitadores matemáticos explícitos y entornos whitelisted; un comando de texto TeX legítimo `\\textbf{Resultado}` fuera de math queda escapado a glifos literales y ya no formatea negrita. `test_text_render_strategy` prueba prosa/matemáticas, no este caso. No se afirma que el PDF fuente conserve habitualmente comandos TeX ni que el proveedor siempre los entregue.
- **Required:** NADR-F17BIS-06 §5.2 **R5–R8**, que exige conservar macros/TeX legítimo, no solo spans de math; el mismo NADR usa `\\textbf{...}` como ejemplo de sintaxis válida.
- **Decision:** el contrato exige distinguir prosa literal de macro legítima; aún no fija qué parser, whitelist o convención debe hacerlo.
- **Consecuencia:** cuando la entrada contiene TeX legítimo fuera de math, la representación estructural se pierde de forma determinista; no se infiere un defecto de protección math ya cubierta.
- **Severidad:** **P1 LOCAL OPEN → GAP-0.6-03**. Destino: ADR Maestro/Execution Plan; falsador puro con macro conocida y prueba de no interpretar texto malicioso.

## 14. GAPS CONSOLIDADOS — SEGUNDA PASADA

| GAP | Observed → Required y consecuencia | Evidencia | Estado y destino |
|---|---|---|---|
| **GAP-0.6-01** | CODE y TABLE admitidos salen como TeX crudo; el contenido literal puede ser interpretado o rechazado, contra el mandato de supervivencia de código y protección contextual NADR-F17BIS-06 R5–R7. | **E-0.6-025**, E-013/032 | **P1 LOCAL · OPEN** → ADR Maestro/Execution Plan; testigo de literalidad focal |
| **GAP-0.6-02** | El render de HEADING descarta nivel/depth antes de crear TeX; contra jerarquía estética y linaje exigidos por PROJECT_SCOPE/ENGINEERING_PRINCIPLES. Distinto de GAP-0.3-01 sobre firma. | **E-0.6-026**, E-014 | **P1 LOCAL · OPEN** → ADR Maestro/Execution Plan; testigo H1/H2 |
| **GAP-0.6-03** | `TextRenderStrategy` escapa macros TeX legítimas fuera de math, por ejemplo `\\textbf{...}`, contraviniendo NADR-F17BIS-06 R5–R8. | **E-0.6-027**, E-012/029 | **P1 LOCAL · OPEN** → ADR Maestro/Execution Plan; testigo TeX legítimo |

**No promover por analogía:** (a) E-028 es la consecuencia G5 del **GAP-0.2-02** upstream (dimensiones); se mantiene allí la autoridad principal hasta reconciliación del alcance; (b) `os.replace` pre-COMMIT no es por sí mismo defecto: G5/2 documenta la regeneración y fencing tras crash; (c) `%PDF-`+COMPLETED es un gate operacional deliberadamente acotado y `scientific_status=NOT_CERTIFIED`; el gate científico corresponde a PPPR.0.8/0.9; (d) `DEGRADED` exige caracterizar PASSTHROUGH, TRANSLATE y provenance antes de abrir GAP nuevo.

**GAPs antecedentes no subsanados por esta auditoría:** PPPR.0.2 (perfiles/geometry), PPPR.0.3 (identidad/canonización), PPPR.0.4 (modelo/prompt/budget) y PPPR.0.5 (W06/leases/sweeper) mantienen sus destinos. No se reasignan aquí.

## 15. HIPÓTESIS — CLASIFICACIÓN DE SEGUNDA PASADA

| ID | Pregunta y falsador específico | Estado |
|---|---|---|
| **H-0.6-A** | ¿CODE/TABLE crudos contienen caracteres o comandos que TeX interpreta en vez de presentar literalmente? | **CONFIRMADA BRECHA POR COMPOSICIÓN** E-025 → GAP-01; ejemplos estáticos, sin ejecución de Tectonic |
| **H-0.6-B** | ¿HEADING pierde jerarquía tipada antes del TeX? | **CONFIRMADA** E-026 → GAP-02; pérdida del nivel, no de existencia del nodo |
| **H-0.6-C** | ¿Se preservan math delimitados y macros legítimas? | **PARTIAL** E-012/027/029; math explícito protegido, TeX textual legítimo fuera de math incumple R5–R8 → GAP-03; semántica no verificada |
| **H-0.6-D** | ¿A4 fijo y 612×792 preservan geometría para figuras? | **PROPAGACIÓN CONFIRMADA** E-028/033 de GAP-0.2-02 (ancho ausente); tolerancia de layout real NO VERIFICABLE → DQ-0.6-02 |
| **H-0.6-E** | ¿La ventana `os.replace`→COMMIT se recupera? | **CONTENCIÓN POR CÓDIGO** E-018/019/031, G5/2 testigo NOT_RUN; fallos físicos NO VERIFICABLE → DQ-0.6-03 |
| **H-0.6-F** | ¿DEGRADED mezcla missing PASSTHROUGH y TRANSLATE y qué llega al operador? | **ABIERTA** E-007/008/030: falta cotejar productor de payload original, cobertura G3 y telemetría/contrato de aceptación antes de clasificar GAP → DQ-0.6-04 provisional |
| **H-0.6-G** | ¿B02.5 e IMAGE preservan activos verificables? | **CONFIRMADA INTEGRIDAD DE BYTES**, E-015/016/023; detección general de fórmulas y fidelidad visual real NO VERIFICABLE → DQ-0.6-01 |
| **H-0.6-H** | ¿Compila Tectonic en español/Unicode/math bajo condiciones reales? | **NO VERIFICABLE** sin compilador/corpus real: DQ-0.6-01 → PPPR.0.8 |
| **H-0.6-I** | ¿El gate final certifica ciencia/layout? | **RECHAZADA COMO GARANTÍA** E-002/024: solo FSM+header; `NOT_CERTIFIED` explícito, validación científica diferida a PPPR.0.8/0.9 |


### 15.1 Deferred Questions provisionales (NO VERIFICABLE / pendientes)

| ID | Razón y no-bloqueo de segunda pasada | Destino |
|---|---|---|
| **DQ-0.6-01** | Tectonic real, UTF-8/acentos, fórmulas, figuras y PDF visual/semántico necesitan insumos y ejecución autorizados; tests fake NOT_RUN, no demuestra calidad en corpus | PPPR.0.8/0.9; no bloquea identificar contratos de render |
| **DQ-0.6-02** | Tolerancia geométrica legítima, page_width por página y drift de figura* no se miden; misma raíz que GAP-0.2-02 | ADR Maestro y PPPR.0.8; no duplicar GAP upstream |
| **DQ-0.6-03** | Crash físico entre rename/COMMIT y recuperación SIGKILL/power loss no ensayados; testigos G5 offline solo leídos | PPPR.0.7 (entorno) / PPPR.0.8 (testigo focal) |
| **DQ-0.6-04** | Falta discriminar ausencia normal PASSTHROUGH vs pérdida de proyección TRANSLATE y destino observable de `AssemblyReport.DEGRADED`; no basta 5% para confirmar defecto | Próxima pasada PPPR.0.6 y ADR Maestro si resulta decisión |

### 15.2 Decision Candidates preliminares (no aprobados)

| ID | Pregunta futura | Autoridad |
|---|---|---|
| **DC-0.6-01** | Distinguir con fidelidad contenido **literal** CODE/TABLE de comandos TeX **legítimos** y delimitadores math; sin parser/renderer nuevo prescrito | ADR Maestro PPPR → Execution Plan |
| **DC-0.6-02** | Contrato de preservación de niveles y representación tipográfica de HEADING según layout/AST, sin exigir pixel-perfect por reflejo | ADR Maestro PPPR → Execution Plan |
| **DC-0.6-03** | Tratamiento del perfil de página/figuras y evidencia suficiente de publicación científica; reconciliar con upstream PPPR.0.2 y downstream PPPR.0.8 | ADR Maestro PPPR → Execution Plan según necesidad |

## 16. RESPUESTAS AL MANDATO — SEGUNDA PASADA

Hay una sola ruta G5 compartida entre foreground y daemon; el compilador físico se invoca en directorio efímero y publica un artefacto privado con CAS antes de promocionarlo. La preservación STEM tiene mecanismos verificables de fragmentos math e imágenes por SHA, pero **no** se certifica equivalencia científica ni visual de PDF→PDF. La segunda pasada confirmó tres discrepancias tipadas: literal CODE/TABLE sin protección contextual, jerarquía HEADING descartada y macros TeX legítimas de texto escapadas. Se preservan como hallazgos locales por separado de la geométrica upstream (GAP-0.2-02) y del gate científico de PPPR.0.8. No se presume ejecución de TeX, duplicación de artifacts ni corrupción física observada.

## 21. CIERRE DEL HITO — IN_PROGRESS

**NO FROZEN — IN_PROGRESS v1.0.1.** Segunda pasada: **34 E-IDs (3 P1, 31 P2)**, tres fichas P1 extendidas, tres GAP locales OPEN, nueve hipótesis clasificadas parcial/terminal, cuatro DQ y tres DC provisionales. Pendiente: cerrar H-0.6-F (degradación y observabilidad), reconciliar no-regresión F17BIS/PPPR, precisar límites de macro/TeX frente a fuente PDF y pasar checklist §8.1–8.2. No hubo tests, Tectonic, Docker, ejecución LLM, SQLite de usuario, corpus ni código de producción.

**Política Git:** abrir PR interno **Draft** exclusivamente de este Markdown desde `pppr/hito-0.6` hacia `pdf-pdf-product-readiness`. Mantener PR general #66 Draft; `main` intacto. No modificar implementación ni ejecutar pruebas científicas sin autorización; tras cierre FROZEN y aprobación, integrar, verificar, eliminar rama corta y comenzar PPPR.0.7 desde el HEAD general nuevo.
