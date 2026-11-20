# HITO_PPPR.0.6_G5_ENSAMBLADO_Y_PDF_SALIDA.md

**Estado:** IN_PROGRESS v1.0.3  
**Fecha de emisión:** 2026-11-19  
**Congelamiento:** N/A  
**Tipo:** Forensic Flow Audit — G5, representación TeX, compilación y salida PDF  
**Iniciativa:** PPPR, Fase 0 de auditoría documental transversal; no altera fases del roadmap.  
**Baseline productivo:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42` (no modificar).  
**Baseline de gobernanza:** `pdf-pdf-product-readiness@30175a0fbdd2774bc1a4ef00d83e57c96a16fa7d` (PPPR.0.1–0.5 FROZEN).  
**Mandato:** inspeccionar la ruta seleccionada G3→G5→PDF: contexto/AST/proyecciones, validaciones y degradación, jerarquía de nodos, ecuaciones/TeX, tablas/código, imágenes/activos, perfil y geometría, Tectonic, lease/FSM/FS, publicación, recuperación y garantías verificables. Separar integridad operativa de fidelidad científica.  
**Metodología superior:** `docs/architecture/1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` v1.3.0 FROZEN; `docs/architecture/1.2_METH_FOR_FORENSIC_HITOs.md` v1.2.0 FROZEN; `PROJECT_SCOPE.md` y `ENGINEERING_PRINCIPLES.md`. D-1/D-2, Atlas de ruta única y PPPR.0.1–0.5 FROZEN.  
**Precedencia y estado:** D-1/D-2, Atlas de ruta única v1.0.2 **DESCRIPTIVO** (corte 6818e86), código `main@1d21cfe`, `docs/architecture/{PROJECT_SCOPE,ENGINEERING_PRINCIPLES}.md`, ADR/NADR FROZEN aplicables (F18). NADR-F17BIS-09 es FROZEN, pero solo su frontera compatible §5.2 aplica al G5 actual; §5.1 de Event Log exclusivo requiere reconciliación con F18. NADR-F17BIS-06 está **PROPOSED**, no aporta MUST vigente. P6 F17-BIS es historia multirruta, no patrón principal.  
**Carácter de la evidencia:** código de repositorio y pruebas versionadas leídas, **NOT_RUN**. No se ejecutaron Tectonic, Docker, APIs, SQLite, corpus ni PDF científico. No se afirma `PRODUCT_READINESS=PASS`.

### Changelog

| Versión | Fecha | Alcance |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-11-19 | Apertura desde merge #70, 24 E-IDs preliminares, 9 hipótesis de contraste y ninguna promoción automática de defectos históricos P6; auditoría read-only G5/compilación/artefactos. |
| 1.0.1-IN_PROGRESS | 2026-11-19 | Segunda pasada: 34 E-IDs, 3 fichas P1 locales y 3 GAP OPEN sobre CODE/TABLE literal, semántica HEADING y macros TeX legítimas fuera de math. H-0.6-A/B confirmadas, C/D/E/F/G/H/I delimitadas; antecedente GAP-0.2-02 y P6 reconciliados. Testigos NOT_RUN, sin FROZEN ni implementación. |
| 1.0.2-IN_PROGRESS | 2026-11-19 | Tercera pasada de H-0.6-F: 42 E-IDs, 3 GAP P1 OPEN sin cuarto GAP precipitado, 9 hipótesis clasificadas, 4 DQ y 4 DC. Cobertura G3-B3/3b, repositorio fallback legacy y señal condicional AssemblyReport contrastados; NOT_RUN, no FROZEN. |
| 1.0.3-IN_PROGRESS | 2026-11-19 | Corrección de autoridad a pedido del owner: Atlas D-1/D-2 y código HEAD son primarios; NADR-F17BIS-06 PROPOSED deja de fundamentar GAP. E-027 se reclasifica a P2 y GAP-0.6-03 se retira como GAP confirmado conservando ID y traza. Dos GAP P1 OPEN sustentados por alcance/principios actuales; NOT_RUN y NO FROZEN. |

## 1. RESUMEN EJECUTIVO

El G5 soportado recibe un documento `READY_FOR_ASSEMBLY` desde el flujo CLI→OCR→G3, o es reclamado por el daemon ensamblador. Ambas composiciones utilizan `AssemblerWorkerDaemon._process_assembly_task`, `AssemblyLeaseRepository`, `CQRSAssemblyContextResolver`, `DocumentAssembler`, `CompilationService`, `HostTectonicRunner` y publicación fenced. La ruta actual **no** reproduce el bypass histórico del servicio, el falso DockerRunner ni la escritura principal del compilador en `os.getcwd()`.

**Garantías observables, todavía limitadas:** validación de secuencia y unicidad antes de OMIT, materialización de proyecciones por generación/versión, fallback con comprobación SHA cuando procede, perfil SQLite durable, bundle de imágenes por digest, escapado de prosa separado de spans matemáticos, ejecución Tectonic aislada por intento y exclusión de publish por owner/lease caducado. `%PDF-` + FSM `COMPLETED` constituyen una comprobación **operativa mínima**, nunca certificación de layout, fórmulas o calidad lingüística `en→es`.

**Hallazgos vigentes:** **GAP-0.6-01** (CODE/TABLE literal entra como TeX crudo) y **GAP-0.6-02** (HEADING pierde nivel en render) siguen **P1 LOCAL OPEN**, sustentados por alcance y principios actuales. El escaper sí transforma macros textuales fuera de math (E-027), pero **GAP-0.6-03 fue retirado como GAP confirmado**: su MUST específico se tomó de NADR-F17BIS-06 **PROPOSED** y no se acreditó que macros de estilo extraídas de PDF deban ejecutarse como TeX. No se observó Tectonic real.

**Veredicto de autoridad:** **IN_PROGRESS v1.0.3**, 42 E-IDs (2 P1/40 P2), dos GAP P1 OPEN y un ID de GAP histórico retirado con justificación. Falta checklist §8.1–8.2; ni FROZEN ni `PRODUCT_READINESS=PASS`.

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

- **Observed:** implementación textual de `main@1d21cfe` y contratos de tests versionados. Un test leído **no** es un test ejecutado; un PDF con magic header **no** es evidencia de preservación visual o científica.
- **Required:** `docs/architecture/PROJECT_SCOPE.md` §§2/4 exige código y fórmulas intactas y jerarquías estéticas; `docs/architecture/ENGINEERING_PRINCIPLES.md` §§II/IV exige linaje y cero degradación silenciosa. F18 gobierna autoridad y recuperación. NADR-F17BIS-09 FROZEN solo se aplica en su parte compatible (§5.2); su §5.1 requiere reconciliación con F18. NADR-F17BIS-06 sigue PROPOSED, no norma aprobada.
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

**Fuentes CLASIFICADAS:** `docs/architecture/adr/pipeline-stabilization/handoff/ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md` v1.0.2, AS-IMPLEMENTED DESCRIPTIVO de D-1/D-2; `docs/architecture/{PROJECT_SCOPE,ENGINEERING_PRINCIPLES}.md`; PPPR.0.1–0.5 FROZEN y NADR F18 vigentes. NADR-F17BIS-06 v1.0.0 **PROPOSED** (sin fuerza normativa); NADR-F17BIS-09 v1.0.0 **APPROVED/FROZEN** (solo §5.2 compatible); HITO P6 F17-BIS histórico. Tests B02/B03/G5 solo leídos, NOT_RUN.

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

## 10. REGISTRO DE EVIDENCIA FORENSE — TERCERA PASADA (NO FROZEN)

| E-ID | Sev. inicial | Observed (archivo::símbolo) | Required/Decision/límite | Disposición |
|---|---|---|---|---|
| **E-0.6-001** | P2 | `pdf_product.py::run_admitted_pdf` ejecuta solo la rama G5 si FSM READY_FOR_ASSEMBLY; para COMPLETED verifica PDF sin reconstruir. | Ruta única/estado operacional D-1/D-2; no implica calidad visual. | OBSERVADO |
| **E-0.6-002** | P2 | `pdf_product.py::preflight_product_run` exige Tectonic y tres bases; `_verify_published_pdf` requiere regular, tamaño mínimo y prefijo `%PDF-`. | Precondición y predicado de éxito **operativos**, no validador integral PDF ni benchmark. | OBSERVADO |
| **E-0.6-003** | P2 | `pdf_product.py::_run_g5` y `apps/compiler/__main__.py::main` inyectan `CompilationService`, `DocumentAssembler`, `SQLiteProfileStore`, `CQRSAssemblyContextResolver`, `HostTectonicRunner`. | Ruta D-1/D-2 y Atlas §3.3; bypass histórico P6-H01 no vigente. NADR-F17BIS-06 PROPOSED no se usa como MUST. | RECONCILIACIÓN |
| **E-0.6-004** | P2 | `AssemblerWorkerDaemon::_process_assembly_task` reclama tarea y hace heartbeat de conexión dedicada; compila a `.assembly_<uuid>.pdf` y usa `leases.publish`. | Contrato G5/2 de autoridad y artefacto privado; no prueba compilar documento científico real. | OBSERVADO |
| **E-0.6-005** | P2 | `AssemblyLeaseRepository::claim/advance/publish` liga `owner/execution_id/TTL` a queue.db y FSM adjunta, con CAS antes de publish. | F18 autoridad/attempt; no asumir cancelación física de Tectonic. | OBSERVADO |
| **E-0.6-006** | P2 | `CQRSAssemblyContextResolver::resolve` valida AST completo, unicidad y continuidad `sequence_id` antes de excluir OMIT; usa `projection_version=1` y generación AST. | Contrato NADR-06 de secuencia íntegra y no falsos gaps tras OMIT. | OBSERVADO |
| **E-0.6-007** | P2 | `DocumentAssembler::assemble` acepta completo o DEGRADED si faltan hasta 5 % de proyecciones con `allow_fallback=True`, rechaza más. | Política de aceptación explícita; no equiparar DEGRADED a fidelidad ni disponibilidad de payload. | OBSERVADO |
| **E-0.6-008** | P2 | `CompilationService::compile_document_with_assets` busca proyección por nodo o `get_verified_payload` con `chunk_id/payload_sha256` y falla ante falta/drift. | Fallback criptográficamente verificado cuando hay datos; calidad científica no evaluada. | OBSERVADO |
| **E-0.6-009** | P2 | `SQLiteProfileStore::save/get` guarda layout/tipo con SHA por documento en `documents.db` y rechaza tampering/replay conflict. | Perfil durable de OCR→G5, no fuente de geometría física exacta. | OBSERVADO |
| **E-0.6-010** | P2 | `RenderGeometryAdapter::extract` normaliza `bboxes` con fallback **612×792 pt**; hay `page_number=metadata.pages[0]`. | Geometría real por página no garantizada; relacionar con GAP-0.2-02 sin duplicar por homonimia. | H-0.6-D |
| **E-0.6-011** | P2 | `RenderContextFactory::create` elige article A4 una/dos columnas usando perfil; registra estrategias por `ContentNodeType`. | No reconstruye por sí mismo el layout físico de la fuente. | OBSERVADO |
| **E-0.6-012** | P2 | `TextRenderStrategy::render` escapa prosa y conserva spans explícitos de matemática; testigos B02.4 comparten delimitadores. | PROJECT_SCOPE §4 exige fórmula invariante, no prueba semántica STEM; NADR-F17BIS-06 es solo antecedente PROPOSED. | OBSERVADO / TESTIGO |
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
| **E-0.6-025** | **P1** | `FlatASTBuilder` admite CODE/TABLE; RenderContextFactory envía esos tipos a `PassthroughRenderStrategy`; el contenido crudo se concatena por `TexBuilder`. | `docs/architecture/PROJECT_SCOPE.md` §4 exige preservar bloques CODE intactos y `ENGINEERING_PRINCIPLES.md` §IV prohíbe degradación silenciosa; `_`, `%`, `&` en texto literal se interpretan como TeX sin protección. NOT_RUN. | **GAP-0.6-01 OPEN** |
| **E-0.6-026** | **P1** | `HeadingPayload.heading_level` admite H1/H2/H3 y `ASTNode.depth` registra jerarquía; `FlatASTBuilder` la transporta. `DefaultRenderUnitMapper` pasa solo node_id, tipo, texto, geometría y activo; `RenderContextFactory` usa `TextRenderStrategy` idéntica para HEADING/PARAGRAPH y `TexBuilder` nunca emite `\\section`/`\\subsection` por nivel. | `PROJECT_SCOPE.md` §2 exige alineación de jerarquías estéticas y §4 topología rastreable; `ENGINEERING_PRINCIPLES.md` §§II/IV exige linaje de depth/parent. El nivel no llega al TeX: dos headings con textos idénticos H1/H2 son visualmente indistinguibles salvo comentarios no tipográficos. | **GAP-0.6-02 OPEN** |
| **E-0.6-027** | P2 | `TextRenderStrategy` conserva math delimitado, pero `LatexEscaper` transforma barras y llaves fuera de esos spans; `\textbf{...}` de texto se imprime literal. | La regla concreta para conservar macros textuales fuera de math está en NADR-F17BIS-06 PROPOSED; no se acreditó que el PDF actual transporte eso como marcado ejecutable. Observed ≠ Required. | **OBS / GAP-0.6-03 RETIRADO → DQ-0.6-01** |
| **E-0.6-028** | P2 | `RenderGeometryAdapter` normaliza anchos con **612 pt**, y `AdaptiveFloatStrategy` usa `relative_width > 0.6` para decidir `figure*` vs `figure` en dos columnas; PyMuPDF conoce el ancho real, pero `NodeMetadata` no lo traslada. | Consecuencia downstream específica del mismo déficit de ancho que **GAP-0.2-02**: figura de 300pt en página 400pt debería resultar 0.75, pero el adapter da 0.49. **No duplicar GAP** hasta decidir si el contrato de layout exige fidelidad exacta; ejemplo estático sin PDF probado. | PROPAGACIÓN DE GAP-0.2-02 |
| **E-0.6-029** | P2 | `core/normalization/explicit_math.py` detecta `$...$`, `$...$`, `\\(...\\)`, `\\[...\\]` y entornos enumerados; falla ante delimitadores desequilibrados, pero no infiere fórmulas de OCR o TeX no explícito. | Falsación parcial de H-0.6-C: protección de spans delimitados no implica reconstruir todas las fórmulas STEM ni cubrir fuentes Unicode. La matemática visual B02.5 es ruta distinta de IMAGE. | H-0.6-C PARCIAL |
| **E-0.6-030** | P2 | `DocumentAssembler` permite `DEGRADED` con hasta 5% de proyecciones ausentes y `allow_fallback`; `CompilationService` usa `get_verified_payload` de `original_chunks` pero solo propaga TeX/activos, no `AssemblyReport.status`. | `AssemblyExecutionContext` aclara que «missing» incluye PASSTHROUGH sin traducción. Queda sin demostrar que se publique una traducción incompleta por la ruta G3 normal; evaluar telemetría y política antes de un GAP de degradación silenciosa. | H-0.6-F ABIERTA |
| **E-0.6-031** | P2 | `AssemblyLeaseRepository.publish` valida artefacto privado, bloquea writer SQLite, actualiza queue/FSM, realiza `os.replace` y recién luego COMMIT; `recover_expired` reencola intento no terminal con CAS y epoch. | F17BIS-09 §5.2 R6/7 y F18 delimitan aislamiento/fencing; `test_g5_assembler_lease_recovery` incluye casos de rollback y promoción completa antes del commit, **NOT_RUN**. No garantizar atomicidad FS+SQL ni recuperación física universal. | H-0.6-E DELIMITADA |
| **E-0.6-032** | P2 | `PyMuPDFProvider.capabilities.has_tables=False`; no afirmar extracción nativa universal de tablas. `FlatASTBuilder._TYPE_MAPPING` acepta tipos `TABLE_SIMPLE/TABLE_COMPLEX/CODE_BLOCK` si el clasificador los produce. | GAP-0.6-01 es un defecto del **consumidor G5 para tipos admitidos**, no una frecuencia acreditada en corpus ni garantía de que cada tabla del PDF sea detectada. | LÍMITE DE ALCANZABILIDAD |
| **E-0.6-033** | P2 | `RenderContextFactory` decide layout solo por `PageLayout.DOUBLE_COLUMN`; `LatexPreambleBuilder` fija A4/11pt y `TexBuilder` no consume geometría para prosa/tablas. El único uso actual de ancho relativo es el float IMAGE. | La reconstrucción física no equivale a copiar cada coordenada; falsación H-0.6-D requiere política explícita de tolerancia, no promesa de pixel-perfect sin corpus. | LAYOUT LIMITADO |
| **E-0.6-034** | P2 | En los testigos `test_text_render_strategy`, `test_b024_g3_g5_math_roundtrip` y `test_b022_image_rendering` se verifican matemáticas delimitadas, prosa e IMAGE; no se ve falsador de CODE/TABLE crudo ni render por `heading_level` en esos archivos. `test_b03_foreground_pdf_product` usa PDF sintético con prefijo PDF. | Contrato parcial en fuentes leídas, **NOT_RUN**; la ausencia de test local no se presenta como fallo ejecutado ni como censo exhaustivo de toda la suite. | TESTIGOS ACOTADOS |
| **E-0.6-035** | P2 | Las dos composiciones G5 fijan AssemblyPolicy(tolerance_ratio=0.05,allow_fallback=True,degradable_failures=frozenset()). DocumentAssembler cuenta nodos sin proyección CURRENT, no tokens, traducciones fallidas ni páginas. | Umbral exacto: 1/20 = 5% admite política; 1/19 >5% rechaza. No extrapolar tasa física. | H-F: POLÍTICA |
| **E-0.6-036** | P2 | AssemblyExecutionContext.missing_node_ids incluye PASSTHROUGH/KEEP_ORIGINAL sin proyección; DocumentAssembler no clasifica estrategia al contar; degradable_failures existe en la configuración pero no es consultado por assemble. | DEGRADED no es sinónimo de traducciones perdidas, y un parámetro de política no demuestra ruta comercial habilitada. | H-F: SEMÁNTICA |
| **E-0.6-037** | P2 | validate_chunk_coverage exige todos los nodos no OMIT con texto, incluidos PRESERVE; materialize_node_results recompone todos los miembros y publish_staged_plan escribe proyecciones de la generación completa solo con recibos validados; la FSM se habilita para G5 después de finalización. | En la ruta coherente G3→G5 no hay por diseño nodos ensamblables sin proyección CURRENT. No se excluye borrado, daño o deriva posterior. | CONTRASTE G3/5 |
| **E-0.6-038** | P2 | CompilationService usa node.control_plane.chunk_id y payload_sha256 para get_verified_payload. El AST del root OCR nace sin esas claves; el enriquecedor añade context_id, no chunk_id. OCR no invoca SQLiteDocumentRepository.save_batch, que sí aparece en TranslationPipeline.execute de la ruta legacy. | No hay productor acreditado de original_chunks conectado a la ruta seleccionada; no se niega otra integración externa. Si el registro/hash no existe, el fallback falla cerrado. | FALLBACK LATENTE |
| **E-0.6-039** | P2 | DocumentAssembler puede decidir DEGRADED y emitir AssemblyReport si el ratio es >0 y <=0.05. CompilationService acepta la decisión pero retorna solo TeX/assets, descartando status/audit_report; el worker solo registra G5_ASSEMBLER_PDF_PUBLISHED y la CLI devuelve COMPLETED/NOT_CERTIFIED. | Señal de degradación perdida SI una entrada con fallback SHA válido llegase a publicación. Contrato SRE §IV de no degradar silenciosamente: tensión condicional sin alcance productivo probado, no cuarto GAP. | DC-0.6-04 / DQ-04 |
| **E-0.6-040** | P2 | test_assembler.test_degraded_assembly_with_missing_projections usa 1/3 ausentes pero tolerancia artificial de 50%; test_g5_assembler_lease_recovery.test_missing_projection_blocks_real_g5_worker_before_pdf usa 1/1 ausente (100%), rechazado antes de fallback. | Testigos NOT_RUN, ninguno acredita un PDF DEGRADED en el límite operativo 5%. | COBERTURA DE TESTIGO |
| **E-0.6-041** | P2 | SQLiteDocumentRepository.get_verified_payload exige fila original_chunks(job_id,chunk_id), hash almacenado igual al esperado y SHA real sobre bytes. Ausencia o deriva se convierten en ASTConsistencyError antes de invocar Tectonic. | La tolerancia porcentual no elude la verificación criptográfica ni autoriza texto original arbitrario. | FAIL-CLOSED |
| **E-0.6-042** | P2 | AssemblyReport.failure_reasons/missing_projection_nodes/degradation_applied no llega a salida física G5. El log de publicación incluye document_id y latency; PDFProductResult comprueba header/FSM y mantiene scientific_status=NOT_CERTIFIED. | Si se decide admitir DEGRADED en producto, hará falta una señal auditable; no se ha observado dicha ejecución en el root soportado. | LÍMITE / DC-04 |

**Severidad v1.0.3:** 42 E-IDs estables: **2 P1 (E-025/026), 40 P2**. Se registra explícitamente la reclasificación E-027 P1→P2 por autoridad PROPOSED, sin borrar el ID ni su Observed; el GAP-0.6-03 histórico está retirado como GAP activo. E-039/042 siguen condicionales y ningún P0/incidente se afirma.

### Fichas P1 vigentes y ficha histórica reclasificada (§4.7)

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
- **Required:** `docs/architecture/PROJECT_SCOPE.md` §4 exige código intacto por passthrough, principios §IV impiden degradación silenciosa. NADR-F17BIS-06 está PROPOSED y no se usa como autoridad vigente.
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

#### E-0.6-027 — observación P2 reclasificada por autoridad en v1.0.3

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
- **Required:** NADR-F17BIS-06 R5–R8 menciona macros textuales, pero **PROPOSED** no establece un MUST vigente. PROJECT_SCOPE §4 exige preservar fórmulas y código, no determina que una macro de estilo textual extraída de PDF se ejecute como marcado TeX.
- **Decision:** procedencia de macro textual y si representa texto literal o marcado autorizado quedan por decidir solo si la ruta lo requiere; no prescribir parser nuevo.
- **Consecuencia:** cuando la entrada contiene TeX legítimo fuera de math, la representación estructural se pierde de forma determinista; no se infiere un defecto de protección math ya cubierta.
- **Severidad:** **P2 OBS / NO GAP CONFIRMADO**. ID GAP-0.6-03 (emitido v1.0.1) **RETIRADO como GAP activo en v1.0.3**, con traza a DQ-0.6-01/DC-0.6-01.

## 14. GAPS CONSOLIDADOS — RECTIFICACIÓN DE AUTORIDAD

| GAP | Observed → Required y consecuencia | Evidencia | Estado y destino |
|---|---|---|---|
| **GAP-0.6-01** | CODE/TABLE se introducen como TeX crudo, y contenido literal puede mutar o fallar en lugar de preservarse. | **E-0.6-025**, E-013/032 | **P1 LOCAL OPEN** → PROJECT_SCOPE §4/principios §IV; ADR Maestro/Execution Plan |
| **GAP-0.6-02** | El render de HEADING descarta nivel/depth antes de crear TeX; contra jerarquía estética y linaje exigidos por PROJECT_SCOPE/ENGINEERING_PRINCIPLES. Distinto de GAP-0.3-01 sobre firma. | **E-0.6-026**, E-014 | **P1 LOCAL · OPEN** → ADR Maestro/Execution Plan; testigo H1/H2 |
| **GAP-0.6-03 (HISTÓRICO, RETIRADO v1.0.3)** | E-027 observa escape de macro textual; F17BIS-06 R5–R8 es PROPOSED y aplicabilidad de esa macro como marcado PDF→PDF no demostrada. | **E-0.6-027 P2** | **NO GAP ACTIVO**. ID conservado; DQ-0.6-01/DC-0.6-01 |

**No promover por analogía:** (a) E-028 es la consecuencia G5 del **GAP-0.2-02** upstream (dimensiones); se mantiene allí la autoridad principal hasta reconciliación del alcance; (b) `os.replace` pre-COMMIT no es por sí mismo defecto: G5/2 documenta la regeneración y fencing tras crash; (c) `%PDF-`+COMPLETED es un gate operacional deliberadamente acotado y `scientific_status=NOT_CERTIFIED`; el gate científico corresponde a PPPR.0.8/0.9; (d) `DEGRADED` exige caracterizar PASSTHROUGH, TRANSLATE y provenance antes de abrir GAP nuevo.

**GAPs antecedentes no subsanados por esta auditoría:** PPPR.0.2 (perfiles/geometry), PPPR.0.3 (identidad/canonización), PPPR.0.4 (modelo/prompt/budget) y PPPR.0.5 (W06/leases/sweeper) mantienen sus destinos. No se reasignan aquí.

## 15. HIPÓTESIS — CLASIFICACIÓN DE TERCERA PASADA

| ID | Pregunta y falsador específico | Estado |
|---|---|---|
| **H-0.6-A** | ¿CODE/TABLE crudos contienen caracteres o comandos que TeX interpreta en vez de presentar literalmente? | **CONFIRMADA BRECHA POR COMPOSICIÓN** E-025 → GAP-01; ejemplos estáticos, sin ejecución de Tectonic |
| **H-0.6-B** | ¿HEADING pierde jerarquía tipada antes del TeX? | **CONFIRMADA** E-026 → GAP-02; pérdida del nivel, no de existencia del nodo |
| **H-0.6-C** | ¿Se preservan math delimitados y macros legítimas? | **PARCIAL/NO VERIFICABLE**: math delimitado protegido; TeX textual fuera de math se escapa, pero F17BIS-06 PROPOSED no impone interpretarlo como comando; evidencia E-012/027/029 → DQ-0.6-01 |
| **H-0.6-D** | ¿A4 fijo y 612×792 preservan geometría para figuras? | **PROPAGACIÓN CONFIRMADA** E-028/033 de GAP-0.2-02 (ancho ausente); tolerancia de layout real NO VERIFICABLE → DQ-0.6-02 |
| **H-0.6-E** | ¿La ventana `os.replace`→COMMIT se recupera? | **CONTENCIÓN POR CÓDIGO** E-018/019/031, G5/2 testigo NOT_RUN; fallos físicos NO VERIFICABLE → DQ-0.6-03 |
| **H-0.6-F** | ¿DEGRADED mezcla missing PASSTHROUGH y TRANSLATE y qué llega al operador? | **CERRADA PARA EL PERÍMETRO ESTÁTICO** E-035…042: ratio cuenta ambos; G3 publica íntegro; fallback SHA con origen legacy no conectado y sin fila falla cerrado. Si un productor válido habilitara DEGRADED, AssemblyReport se perdería; NO VERIFICABLE en root seleccionado → DQ-04/DC-04, no cuarto GAP |
| **H-0.6-G** | ¿B02.5 e IMAGE preservan activos verificables? | **CONFIRMADA INTEGRIDAD DE BYTES**, E-015/016/023; detección general de fórmulas y fidelidad visual real NO VERIFICABLE → DQ-0.6-01 |
| **H-0.6-H** | ¿Compila Tectonic en español/Unicode/math bajo condiciones reales? | **NO VERIFICABLE** sin compilador/corpus real: DQ-0.6-01 → PPPR.0.8 |
| **H-0.6-I** | ¿El gate final certifica ciencia/layout? | **RECHAZADA COMO GARANTÍA** E-002/024: solo FSM+header; `NOT_CERTIFIED` explícito, validación científica diferida a PPPR.0.8/0.9 |


### 15.1 Deferred Questions provisionales (NO VERIFICABLE / pendientes)

| ID | Razón y no-bloqueo de segunda pasada | Destino |
|---|---|---|
| **DQ-0.6-01** | Compilación UTF-8/math y procedencia de macros de texto no matemáticas requieren contrato de entrada y testigo; PDF extraído como prosa no garantiza que `\textbf` sea estilo ejecutable. No bloquea auditoría estática | PPPR.0.8/0.9 y ADR Maestro solo si el canal TeX se requiere |
| **DQ-0.6-02** | Tolerancia geométrica legítima, page_width por página y drift de figura* no se miden; misma raíz que GAP-0.2-02 | ADR Maestro y PPPR.0.8; no duplicar GAP upstream |
| **DQ-0.6-03** | Crash físico entre rename/COMMIT y recuperación SIGKILL/power loss no ensayados; testigos G5 offline solo leídos | PPPR.0.7 (entorno) / PPPR.0.8 (testigo focal) |
| **DQ-0.6-04** | ¿Hay una composición soportada que provea simultáneamente original_chunks verificables y control_plane(chunk_id,payload_sha256) para <=5% de proyecciones ausentes? No se acredita en OCR→G3 actual; sin backing falla cerrado. No bloquea inventario estático, pero impide afirmar un PDF DEGRADED real y su falta de señal | ADR Maestro/PPPR.0.8, testigo focal solo si se mantiene esta capacidad |

### 15.2 Decision Candidates preliminares (no aprobados)

| ID | Pregunta futura | Autoridad |
|---|---|---|
| **DC-0.6-01** | Distinguir con fidelidad contenido **literal** CODE/TABLE de comandos TeX **legítimos** y delimitadores math; sin parser/renderer nuevo prescrito | ADR Maestro PPPR → Execution Plan |
| **DC-0.6-02** | Contrato de preservación de niveles y representación tipográfica de HEADING según layout/AST, sin exigir pixel-perfect por reflejo | ADR Maestro PPPR → Execution Plan |
| **DC-0.6-03** | Tratamiento del perfil de página/figuras y evidencia suficiente de publicación científica; reconciliar con upstream PPPR.0.2 y downstream PPPR.0.8 | ADR Maestro PPPR → Execution Plan según necesidad |
| **DC-0.6-04** | Determinar si DEGRADED con fallback pertenece realmente a la ruta producto. Solo si se habilita: política por clase de fallo y observabilidad verificable de AssemblyReport, sin infraestructura nueva presupuesta | ADR Maestro PPPR → Execution Plan condicionado |

## 16. RESPUESTAS AL MANDATO — SEGUNDA PASADA

Hay una sola ruta G5 compartida entre foreground y daemon; el compilador físico se invoca en directorio efímero y publica un artefacto privado con CAS antes de promocionarlo. La preservación STEM tiene mecanismos verificables de fragmentos math e imágenes por SHA, pero **no** se certifica equivalencia científica ni visual de PDF→PDF. La segunda pasada observó tres conductas tipadas; la revisión v1.0.3 confirmó **dos GAPs vigentes** (CODE/TABLE literal y jerarquía HEADING) y reclasificó **E-0.6-027** (macro de texto escapada) como **OBS P2**, retirando GAP-0.6-03 por autoridad insuficiente del NADR-F17BIS-06 PROPOSED. La geometría upstream conserva su GAP-0.2-02 y el gate científico queda para PPPR.0.8. No se presume ejecución de TeX, duplicación de artifacts ni corrupción física observada.

### 16.1 Resultado focal H-0.6-F (Observed / Required / Decision)

**Observed:** G3-B3/3b exige recibos y proyecciones completas por generación, incluso para PRESERVE. G5 lee esas proyecciones por documento/hash/versión, de modo que una generación íntegra no requiere fallback. Con ausencia posterior, CompilationService busca payload en original_chunks mediante dos claves de control_plane que el root OCR no agrega; sin fila/hash válido aborta con ASTConsistencyError. El repositorio original_chunks sí tiene un productor en TranslationPipeline legacy, pero ese pipeline no es D-1/D-2. DocumentAssembler puede calcular DEGRADED con <=5% ausente y producir AssemblyReport; ese reporte se descarta al devolver únicamente TeX/assets y no es visible en la señal de publicación del worker.

**Required:** PROJECT_SCOPE §4 exige integridad; ENGINEERING_PRINCIPLES §IV prohíbe degradación silenciosa; CompilationService y DocumentAssembler son el flujo implementado D-1/D-2 según Atlas, no una obligación que dependa de F17BIS-06 PROPOSED. Sin SHA válido falla cerrado.

**Decision:** NO se acredita que el root soportado produzca un PDF DEGRADED, así que no se crea GAP-0.6-04 por inferencia. La pérdida de AssemblyReport es una incompatibilidad **condicional** si esa rama se hace alcanzable; DQ-0.6-04 solicita falsador y DC-0.6-04 decide si habilitarla antes de implementar. No es una aprobación de fallback al inglés en un producto en→es.

## 17. RECONCILIACIÓN DE FUENTES Y CONTINUIDAD DE LA RUTA ÚNICA

| Fuente | Estado real comprobado | Utilidad y límite para el G5 actual |
|---|---|---|
| **D-1/D-2 + Atlas** `pipeline-stabilization/handoff/ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md` v1.0.2 | Decisión convergida + **mapa AS-IMPLEMENTED**, corte `6818e86` del 2026-11-13 | Selecciona CLI→OCR→G3→G5, distingue daemon/foreground y R1/R3; **no es NADR ni acredita HEAD automáticamente** |
| **Código `main@1d21cfe`** | Git compare `6818e86…1d21cfe` devuelve **78 rutas cambiadas en conjunto**; entre `apps/`, `core/`, `infra/`, `runtime/`, solo cambiaron `runtime/recovery.py` y `runtime/resumer.py` | Los entrypoints/consumidores principales G5 del Atlas no cambiaron en ese delta; el código efectivamente leído sigue siendo evidencia primaria |
| `docs/architecture/PROJECT_SCOPE.md` §§2/4 y `ENGINEERING_PRINCIPLES.md` §§II/IV | Objetivos de producto y principios de conservación matemática/código, jerarquía visual y linaje | Obligan a evaluar GAP-0.6-01/02 sin depender de propuestas antiguas; no exigen pixel-perfect ni ejecutar todo texto que parezca macro TeX |
| PPPR.0.1–0.5 FROZEN + F18 | Auditorías y decisiones posteriores sobre rutas, identidad, G3, receipts, FSM, leasing y recuperación | Preservar contratos actuales y destinos de GAP upstream; no restablecer journal legacy ni rutas alternativas |
| HITO P6 de F17-BIS | Diagnóstico forense de un compilador antiguo que eludía CompilationService, tenía un DockerRunner engañoso y rutas de I/O compartidas | **HISTÓRICO**: los riesgos justifican inspeccionar, pero no describen el G5 conectado en `main` |
| NADR-F17BIS-06 v1.0.0 | **PROPOSED**, aunque su cuerpo usa MUST R5–R12 | **Sin autoridad normativa vigente**; el antiguo GAP-0.6-03 se retira como GAP confirmado, conservando E-027 y su destino DQ-01 |
| NADR-F17BIS-09 v1.0.0 | **APPROVED — FROZEN**, §5.2 aislamiento de artefactos y §5.1 Event Log exclusivo | §5.2 es compatible con HostTectonicRunner/artefacto privado; §5.1 debe reconciliarse con F18, no se aplica mecánicamente al G5 convergido |

**Regla de evidencia y no-regresión:** Atlas ayuda a localizar el recorrido; HEAD decide qué está conectado; las obligaciones se evalúan según estado formal y frontera. Los testigos de laboratorio con fake y los tests versionados leídos no prueban fidelidad STEM ni operación comercial. Ningún documento histórico se reescribe y ninguna propuesta se eleva a FROZEN por interpretación.

**Corrección registrada, sin pérdida de trazabilidad:** E-0.6-027 conserva su identificador y comportamiento observado, pero cambia de P1 a P2 por falta de norma aprobada aplicable. El ID `GAP-0.6-03` queda **histórico/RETIRADO**, no renumerado ni contado entre los dos GAPs P1 OPEN. Si un contrato futuro requiere macros de texto como sintaxis ejecutable, habrá que reabrir la pregunta con evidencia y decisión, no por automatismo F17-BIS.

## 21. CIERRE DEL HITO — IN_PROGRESS

**NO FROZEN — IN_PROGRESS v1.0.3.** Corrección normativa basada en Atlas D-1/D-2, HEAD actual y F17-BIS: 42 E-IDs (2 P1, 40 P2), 2 GAP P1 OPEN y GAP-03 histórico retirado, 9 hipótesis, 4 DQ y 4 DC. Resta checklist §8.1–8.2 y registrar delta/no-regresión documental. Sin tests, Tectonic, Docker, LLM, corpus o implementación.

**Política Git:** mantener PR interno **Draft** exclusivamente de este Markdown desde `pppr/hito-0.6` hacia `pdf-pdf-product-readiness`. Mantener PR general #66 Draft; `main` intacto. No modificar implementación ni ejecutar pruebas científicas sin autorización; tras cierre FROZEN y aprobación, integrar, verificar, eliminar rama corta y comenzar PPPR.0.7 desde el HEAD general nuevo.
