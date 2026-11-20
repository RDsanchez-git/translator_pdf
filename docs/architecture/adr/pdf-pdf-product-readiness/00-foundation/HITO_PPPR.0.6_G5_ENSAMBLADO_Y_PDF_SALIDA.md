# HITO_PPPR.0.6_G5_ENSAMBLADO_Y_PDF_SALIDA.md

**Estado:** IN_PROGRESS v1.0.0  
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

## 1. RESUMEN EJECUTIVO

El G5 soportado recibe un documento `READY_FOR_ASSEMBLY` desde el flujo CLI→OCR→G3, o es reclamado por el daemon ensamblador. Ambas composiciones utilizan `AssemblerWorkerDaemon._process_assembly_task`, `AssemblyLeaseRepository`, `CQRSAssemblyContextResolver`, `DocumentAssembler`, `CompilationService`, `HostTectonicRunner` y publicación fenced. La ruta actual **no** reproduce el bypass histórico del servicio, el falso DockerRunner ni la escritura principal del compilador en `os.getcwd()`.

**Garantías observables, todavía limitadas:** validación de secuencia y unicidad antes de OMIT, materialización de proyecciones por generación/versión, fallback con comprobación SHA cuando procede, perfil SQLite durable, bundle de imágenes por digest, escapado de prosa separado de spans matemáticos, ejecución Tectonic aislada por intento y exclusión de publish por owner/lease caducado. `%PDF-` + FSM `COMPLETED` constituyen una comprobación **operativa mínima**, nunca certificación de layout, fórmulas o calidad lingüística `en→es`.

**Preguntas activas, aún no GAPs:** tratamiento de CODE/TABLE como TeX crudo, conservación de niveles HEADING, geometría normalizada con ancho/alto fallback fijos, compilación de macros Unicode/fuentes, cobertura de validación física y ventana `os.replace`→commit. Un incumplimiento P1 solo se registrará con consumidor, requisito, causa y consecuencia demostrables, no con intuición.

**Veredicto inicial:** **IN_PROGRESS**. La siguiente pasada debe falsar/confirmar cada hipótesis y cruzar los testigos B02/G5; sin PASS ni solución de diseño anticipada.

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
| Render por tipo, TeX y estructura | `core/compiler/rendering/{context,implementations,mapper}.py`, `apps/compiler/tex_builder.py` | **AUDITADO focal** (E-011…015) |
| Imágenes y materialización física | `core/compiler/rendering/image_assets.py`, `apps/compiler/tectonic_runner.py` | **AUDITADO focal** (E-016/017) |
| Testigos offline | B03, B02.2/B02.4/B02.5, G3/B4.4, G5 lease/worker, TeX renderer/Tectonic | **LEÍDOS · NOT_RUN** (E-021…023) |
| Historia P6 | HITO F17BIS P6 y NADR-F17BIS-06/-09 | **RECONCILIACIÓN POR DELTA**; no reabrir automáticamente P6-H01…04 |
| Calidad real PDF en corpus, GT, producto y despliegue | PPPR.0.8/0.9 y PPPR.0.7 según contrato | **REFERENCIADO / NO VERIFICABLE** |

## 4. FUENTES DE EVIDENCIA

**Código activo fijo:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`: `apps/cli/pdf_product.py`; `apps/compiler/{__main__,tectonic_runner,tex_builder}.py`; `infra/db/{assembly_recovery,profile_store,materialized_repo,document_repository}.py`; `core/compiler/{context_resolver,assembler,service}.py`; `core/compiler/rendering/{mapper,models,context,implementations,image_assets}.py`.

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

## 10. REGISTRO INICIAL DE EVIDENCIA (NO FROZEN)

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

**Severidad preliminar P2** solo registra hechos y preguntas: **ningún GAP P1/P0 adjudicado** en esta apertura. La ausencia de marca de sección en HEADING o la emisión de CODE raw requieren examen con contrato y falsadores antes de clasificarlos.

## 14. GAPS CONSOLIDADOS — APERTURA

**Ningún GAP local formalizado todavía.** Candidatos: E-0.6-013 (CODE/TABLE vs marcado TeX legítimo), E-0.6-014 (jerarquía HEADING), E-0.6-010 (geometría y tamaño de página), E-0.6-018 (crash/publish); se separarán regresiones reales de límites aprobados y upstream GAP-0.2-02.

**GAPs antecedentes no subsanados por esta auditoría:** PPPR.0.2 (perfiles/geometry), PPPR.0.3 (identidad/canonización), PPPR.0.4 (modelo/prompt/budget) y PPPR.0.5 (W06/leases/sweeper) mantienen sus destinos. No se reasignan aquí.

## 15. HIPÓTESIS FALSABLES — IN_PROGRESS

| ID | Pregunta y falsador específico | Estado |
|---|---|---|
| **H-0.6-A** | ¿CODE/TABLE crudos contienen caracteres o comandos que TeX interpreta en vez de presentar literalmente? Falsar con payload real y `PassthroughRenderStrategy`. | **TO BE VERIFIED** |
| **H-0.6-B** | ¿HEADING pierde nivel/jeraquía en TeX por mapearse como prosa sin sección? Rastrear `HeadingPayload`, `RenderUnitMapper` y `TexBuilder`. | **TO BE VERIFIED** |
| **H-0.6-C** | ¿Preservación de matemáticas inline/display cubre delimitadores y macros científicas soportadas? Separar bytes y semántica; inspeccionar `find_explicit_math_spans`. | **TO BE VERIFIED** |
| **H-0.6-D** | ¿La página A4 y geometría 612×792 bastan para trazabilidad de layout de papers de diferente tamaño? Contrastar origen y contrato físico, no exigir clon perfecto sin política. | **TO BE VERIFIED** |
| **H-0.6-E** | ¿La ventana `os.replace`→SQLite COMMIT está correctamente recuperada y fenced en todos los cortes relevantes? Testigos G5/2 y lectura de daemon. | **TO BE VERIFIED** |
| **H-0.6-F** | ¿La política `DEGRADED ≤5 %` más fallback SHA permite perder contenido científico sin advertencia adecuada? Verificar uso y límites, no inferir a partir de umbral. | **TO BE VERIFIED** |
| **H-0.6-G** | ¿La ruta visual math/figuras conserva activos originales y falla cerrada cuando no los obtiene? Considerar límites B02.5 y corpus real. | **TO BE VERIFIED** |
| **H-0.6-H** | ¿Tectonic real compila UTF-8 español, macros y assets con el preámbulo elegido? `--untrusted`/tests fake ≠ cobertura física. | **NO VERIFICABLE preliminar** → futuro PPPR.0.8, si autorizado |
| **H-0.6-I** | ¿Hay validación de topología/fidelidad del PDF final más allá de FSM+header? Distinguir gate operacional de gate científico/visual. | **TO BE VERIFIED** |

## 16. RESPUESTAS INICIALES AL MANDATO

Hay una sola ruta G5 compartida entre foreground y daemon; el compilador físico se invoca en directorio efímero y publica un artefacto privado con CAS antes de promocionarlo. La preservación STEM tiene mecanismos verificables de fragmentos math e imágenes por SHA, pero **no** se certifica equivalencia científica ni visual de PDF→PDF. La ruta de salida TeX exige analizar por tipo la diferencia entre texto literal y marcado deliberadamente ejecutable, y si la jerarquía de encabezados se pierde.

## 21. CIERRE DEL HITO — IN_PROGRESS

**NO FROZEN.** Primera pasada con 24 E-IDs P2, 9 hipótesis (varias abiertas), cero GAPs formalizados y sin revisión final §8.1–8.2. Pendiente: indagar las contradicciones de CODE/TABLE, heading y tamaño de página; verificar fuente de metadatos, macros Unicode/TeX, garantías ante crash, testigos específicos y comparación F17BIS P6; después clasificar hipótesis y abrir GAPs solamente con prueba normativa.

**Política Git:** abrir PR interno **Draft** exclusivamente de este Markdown desde `pppr/hito-0.6` hacia `pdf-pdf-product-readiness`. Mantener PR general #66 Draft; `main` intacto. No modificar implementación ni ejecutar pruebas científicas sin autorización; tras cierre FROZEN y aprobación, integrar, verificar, eliminar rama corta y comenzar PPPR.0.7 desde el HEAD general nuevo.
