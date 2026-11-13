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


## 1.1 Trazabilidad de sujetos: no equiparar commits y ejecuciones

| Evidencia | Sujeto acreditado | Resultado y límites |
|---|---|---|
| C0/T01 | override y bootstrap del PR #46, imagen sha256:abe5b5... | Preflight/config + persistencia entre contenedores en laboratorio descartable; cierre por ratificación del owner, no censo global de ejecutores |
| C1/T02 | misma composición compartida; admisión CLI, OCR independiente | SHA de bytes, AST y plan persistentes con lecturas externas; no prueba de traducción |
| C2/T03–T04 | runtime funcional del PR #46 @ 93a8f9021cbb95c92c9242d68fd6f1dfe9eb3d0f; negativo adicional @ 21eb7da8baf1ac86a288916e112f9e67ca652494 | Daemons independientes y PDF físico; testigo C2 con fake, G5 negativos y selector fail-closed. Acta principal C2; no se ejecutó sobre cada commit documental posterior |
| C3/T05 | c146f0efbb2754484653721e92d6854c51f7ddd8 | 1 passed, 1.66 s, exit 0, Windows; subprocess que abandona antes de FSM final + proceso nuevo recupera; W06/G5 son falsadores focales reutilizados. No reinicio universal |
| C3/T07 | ff277936ee949312ca73f3f183f96fe78d8ea41b | Comparación foreground aislada exit 0, PDF válido; misma identidad/contrato, **no** identidad binaria del PDF |
| C4/T06 | 1b515cb2f93a3121da9682d5024dd4509eb8e47f | Censo de roots versionados y 6 passed, 0.77 s, exit 0; externos UNKNOWN |
| DoD 9/9 | f20b2aaa618726e72b205b241595a98d2112903a | Cotejo documental; logs brutos de C2 no adjuntos al PR |
| Merge | HEAD del PR #46 b01f1ca740db7f048fcb0f3a83505977d27d72af; merge commit 6818e86e21b14e77a606f0c863e9c199b4627601 | Merge a pipeline_stabilization; no merge a main, despliegue ni cutover |

La comparación documental del DoD registra que los blobs OCR/G3/G5/foreground esenciales permanecieron sin modificación funcional desde el testigo C2 hasta el cierre, con aislamiento focal del legacy R1 en CLI. **Eso no constituye una ejecución dinámica de C2 sobre el HEAD final.** Siempre asociar cada PASS al commit y al proceso específicos; preservar diferencias entre resultados del owner, tests de CI, revisión estática y artefactos realmente archivados.

**Precisión sobre los receipts C2:** hubo dos tareas LLM completadas (PRESERVE y TRANSLATE), una tarea ASSEMBLER completada y dos registros receipt; la unidad PRESERVE no transportó respuesta LLM ni produjo POST. No interpretar la cardinalidad de receipts como dos inferencias pagadas.

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

**Cierre administrativo propuesto:** plan de C0–C4 marcado COMPLETADO/MERGED y archivado como registro ejecutado. Ver la [ruta vigente](ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md) y el [runbook](LABORATORIO_Y_REPRODUCCION.md).


## 5. Índice de custodia y condiciones para evidencia futura

- **Fuente primaria:** actas y discusión del PR #46, referenciadas arriba, más los commits exactos; los ZIP históricos G3/G4/G5 y la evidencia host Windows siguen siendo antecedentes de custodia externos a Git, no anexos nuevos de la campaña C0–C4.
- **Ausencias declaradas:** no se adjuntó un volcado íntegro de los logs brutos ni todos los binarios del laboratorio C2 al repositorio; los contadores/hashes/actas no deben describirse como reproducción forense completa independiente.
- **Para una corrida futura:** conservar commit, digests, versión y modelo de Compose, RUN-ID no reciclado, hash de input, hashes AST/manifiesto, IDs de tareas/leases, estados/resultados persistidos, conteo HTTP, PDF hash/estructura, códigos de salida y STOP; separar factibilidad del fixture de cobertura científica. Consultar [runbook](LABORATORIO_Y_REPRODUCCION.md).
- **Retención documental:** no reemplazar ni eliminar actas I0, manifiestos o firmas SHA con un resumen de handoff. El inventario histórico se conserva hasta un censo de referencias y decisión de archivo/borrado independiente.

El siguiente cambio del pipeline debe crear **evidencia nueva sobre su propio SHA**, no heredar una etiqueta PASS de 2026-11-12. El cierre aquí es solo convergencia de topología/control con proveedor simulado.
