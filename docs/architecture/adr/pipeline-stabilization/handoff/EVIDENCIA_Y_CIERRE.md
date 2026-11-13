# Cierre de convergencia PDF→PDF — evidencia y decisiones

**Estado:** CONVERGENCIA_OPERATIVA_ACREDITADA (laboratorio con proveedor fake) y **MERGED** en pipeline_stabilization el 2026-11-13. **No** equivale a PRODUCT_READINESS=PASS. Decisión D-1/D-2 aprobada por owner 2026-11-08.

**Commit de integración:** [6818e86e21b14e77a606f0c863e9c199b4627601](https://github.com/RDsanchez-git/translator_pdf/commit/6818e86e21b14e77a606f0c863e9c199b4627601), PR [#46](https://github.com/RDsanchez-git/translator_pdf/pull/46), HEAD del PR probado b01f1ca740db7f048fcb0f3a83505977d27d72af.

## 1. Testigos y actas

| Hito | Hecho acreditado | Acta |
|---|---|---|
| C0/T01 | Compose real, rutas/volúmenes nuevos, bootstrap UID10001, red interna y fake | [C0](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6838189437) |
| C1/T02 | CLI SHA-256 e inbox compartido, OCR real y AST/plan durables | [C1/C2](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6837871200) |
| C2/T03–T04 | OCR→G3→G5 autónomos, fake HTTP controlado, receipts/publicación y Tectonic físico | [C2](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6837871200) |
| C3/T05 | Crash entre subprocess G3, staged→publicado sin reinferencia; W06 UNKNOWN, G5 fencing y rollback | [T05](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6840272805) |
| C3/T07 | Foreground aislado equivalente en contrato y PDF físico; temporales limpiados, exit 0 | [T07](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6840717576) |
| C4/T06 | Exclusividad de roots productivos versionados, R1 fail-closed, R3 fuera de Compose; 6 PASS/exit 0 | [T06](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6841122597) |
| DoD §8 | Nueve condiciones positivas cotejadas, solo alcance operativo/laboratorio | [DoD 9/9](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6841545770) |
| Integración | Merge de código a pipeline_stabilization separado de producción/cutover | [decisión del owner](https://github.com/RDsanchez-git/translator_pdf/pull/46#issuecomment-6842521268) |

**Naturaleza de la evidencia:** salidas operativas reportadas por owner en Windows/Docker Desktop, inspección del código/actas GitHub; no una reejecución independiente de las máquinas ni anexos completos de logs brutos/PDF.

## 2. Identidades del testigo positivo C2

- Fuente sintética de 1544 bytes: SHA-256 28a53af840244e4022afb08eb800e6348a866b957779e5b5753215afbc158d0f.
- AST hash b0b4cb12ea5e2a871a8789e5228e428b10eca04380e5a95503ff4f61c89f9c4a; manifiesto SHA-256 7724718fd66aff7b570f70a1dad828b2d3391abd14c47ef32fd12fb4a487229d.
- Unidades: isolated_0001_1_c1126087 (PRESERVE) y chunk_0002_2_4_fdbea9ce (TRANSLATE). **PRESERVE sin POST**.
- HTTP fake: 1 intento, 1 POST TRANSLATE aceptado HTTP 200, 0 rechazados; 2 receipts, 1 publicación, 4 proyecciones, 3 tasks completadas; FSM COMPLETED v7.
- PDF Tectonic 7050 bytes, una página, texto extraíble; SHA-256 C2 71f209255c923daef84e44e1ae1bf642dfe5270e862eadedb0709b94ee62bfe3.
- Foreground T07 sobre igual fuente/AST/plan: PDF 7050 bytes, SHA-256 9f70c22525358f7134020ad1ef511067037eca35cfe6636acd2494178a5325b4; equivalencia de **contrato**, no bytes idénticos.
- Imagen usada en laboratorio: sha256:abe5b5dbbc65e8920e0948b189bd9bd090eb395e99420918190128a2ec12b4bd. Proyecto C2 histórico tpdfconvconv1211b; **no** reutilizar su estado para nueva corrida.

## 3. CI heredado y decisión de integración

[CI HEAD PR, run #231](https://github.com/RDsanchez-git/translator_pdf/actions/runs/43350951187): pyright + import-linter **PASS**, unit tests **PASS**, CV SMOKE **FAIL** (BASELINE_INTEGRITY_FAILURE, exit 3: faltan 15 PDFs doc_08…doc_22) e integration tests **FAIL** (3 casos históricos B02_UNREPRESENTED_VECTOR_DRAWING, 66 PASS/3 FAIL). Los mismos fallos estaban en [CI de la rama base, run #180](https://github.com/RDsanchez-git/translator_pdf/actions/runs/42650619034), con fuentes/ci/manifest/test implicados idénticos en Git. El contrato [FASE_6_ENFORCEMENT_CONTRACT.md](../../phase-17-bis/plans/FASE_6_ENFORCEMENT_CONTRACT.md) v1.0.0 ACTIVE §3 trata static-analysis como REQUIRED y CV/integration como informativos durante la transición. El owner aceptó expresamente integrar sin falsear esos dos FAIL. El faltante de corpus se sigue en [issue #34](https://github.com/RDsanchez-git/translator_pdf/issues/34); el problema de expectativas B02 es independiente y pendiente.

## 4. Qué NO queda cerrado ni autorizado

- W09, preservación de ecuaciones/tablas/figuras en corpus heterogéneo, evaluación lingüística con proveedor real, costos y límites productivos, aprobación de operación/rollout/cutover.
- Efecto externo incierto de generaciones históricas: G3_EXTERNAL_UNKNOWN conserva su cuarentena sin retry.
- Llamadores externos a Git de R1/R3 siguen UNKNOWN; NO retirar módulos de compatibilidad por inferencia.
- Atlas AS-IS y Charter DRAFT siguen siendo históricos con fecha/autoridad propias; la etiqueta de convergencia no los convierte en FROZEN ni reemplaza NADR.

**Cierre administrativo propuesto:** plan de C0–C4 marcado COMPLETADO/MERGED y archivado como registro ejecutado. Ver la [ruta vigente](RUTA_CANONICA_PDF_PDF.md) y el [runbook](LABORATORIO_Y_REPRODUCCION.md).
