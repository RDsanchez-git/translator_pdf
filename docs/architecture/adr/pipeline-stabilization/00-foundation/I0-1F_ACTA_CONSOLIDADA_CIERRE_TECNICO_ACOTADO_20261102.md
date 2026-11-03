# I0-1F — Acta consolidada final de cierre técnico acotado: procedencia, reproducibilidad y entrega documental

**Fecha de decisión documental:** 2026-11-02 (zona local de Argentina).  
**Estado:** `I0-1F_CIERRE_TECNICO_DOCUMENTAL_ACOTADO_CON_RESERVAS` — **no cierre pleno del plan rector ni certificación de producción**.  
**Decisión del owner:** aceptación expresa del **expediente documental limitado F3** en esta conversación, seguida de instrucción de emitir **directamente esta única acta consolidada de I0-1F**. No constituye firma digital, aprobación normativa del Architecture Board ni aceptación de propiedades que no fueron demostradas.  
**Plan de referencia:** `I0-1F_PLAN_RECTOR_EJECUCION_SOTA_ACOTADO_v0.1_20261101.md`, F0→F1→F2→F3, aceptado por el owner con autorizaciones separadas para operaciones con efectos laterales.  
**Repositorio / rama de producto:** `RDsanchez-git/translator_pdf` / `pipeline_stabilization`.  
**Ruta editorial prevista:** `docs/architecture/adr/pipeline-stabilization/00-foundation/`. **Publicación Git pendiente**: este archivo no implica `git add`, commit, push, PR ni modificación del checkout.  
**Antecedentes de forma:** actas I0-1C, I0-1D e I0-1E; ninguna se reabre o sustituye.

## 1. Autoridad, sujeto y frontera de cierre

El cierre se circunscribe a la **evidencia efectivamente reunida sobre el sujeto histórico H=R2**, la reconciliación estática de insumos y una entrega documental auditable y liviana. Se adopta la decisión operacional **reuse-first** posterior al plan inicial para no generar imágenes redundantes ni copiar gigabytes de dependencias sin justificación. Este cambio de vía **no convierte en satisfechos** los criterios de reproducibilidad bit a bit o portabilidad independiente del plan original.

| Identidad congelada | Testigo |
|---|---|
| Git HEAD del producto | `d4cda2c379c0efd93a70e795d31c37a0ede7a192` |
| Git tree | `f2a635ef8822780698066a288e46607c8b671938` |
| Imagen histórica H=R2 | `sha256:abe5b5dbbc65e8920e0948b189bd9bd090eb395e99420918190128a2ec12b4bd` |
| Tag de H | `i0-1d/translator-pdf-runtime:r2-d4cda2c-20261031_211824` |
| Padre incremental histórico de H | `sha256:b476a8ceedb67a6843bb8673ba9defd87d939d18d09066b0b428882960a0e302` |
| Plataforma | `linux/amd64`; Python R2 `3.11.17` |
| Capas, dato histórico | H: 35; padre: 25; prefijo común: 25/25 |

La **base OCI nativa de F1** (`sha256:5de4b1c725efc1ab7b9b1410aa5af48b3b5deb1ca6910b749d08168436633146`) es un **material diferente** del padre incremental de H. El candidato **C** de F1 tampoco es H: quedó definido estáticamente, **no construido**. Los hashes son testigos de identidad/integridad local frente a referencias, **no firmas de origen externo**.

## 2. Resultado consolidado del plan F0–F3

| Tramo / pregunta | Resultado adjudicado en el alcance ejecutado | Límite que subsiste |
|---|---|---|
| **F0 — Identidad local** | `PASS_LOCAL_INPUT_IDENTITY_INVENTORY_LIMITED`: HEAD/tree, sellos de fuente, materiales históricos, imagen H y padre identificados; plataforma y prefijo 25/25 documentados. **Tramo cerrado.** | No autenticación externa; no derivar portabilidad o reproducibilidad de la presencia de H. |
| **F1 — Insumos y receta** | `CERRADO_TECNICAMENTE_EN_ALCANCE_ESTATICO_CON_RESERVAS`: HEAD↔ZIP↔CSV **346/346**; índice **160/160 materiales** (158 wheels, lock, Tectonic); **12 blobs OCI** y **142.670.189 bytes** cotejados; receta C con huellas estáticas. BuildKit v0.25.1 fue corroborado después por el operador. | F1-C conserva su `REVIEW_BUILDKIT_IDENTITY_INCOMPLETE_NO_BUILD` original; la receta C no fue ejecutada y su `COPY` del wheelhouse es ineficiente. Los hashes individuales de wheels de D0-14 se **reutilizaron históricamente**, no recalcularon íntegramente en F1-05. Sin autenticidad de atestación in-toto/firma upstream. |
| **F2 — Cold builds / reproducibilidad** | Preflight F2-S00 documentado; **rama documental reuse-first concluida** conservando H y su padre, sin build, pull, exportación ni duplicación. **C1 y C2: `NOT_RUN`**. | **`F2_BITWISE_REPRODUCIBILITY: NOT_DEMONSTRATED`**. No se demostró independencia de cachés/builds fríos. El umbral de 64 GiB fue referencia conservadora de planificación, no requisito físico probado. No declarar F2 original plenamente cumplida. |
| **F3 — SBOM, procedencia, entrega** | F3-S03 R2 produjo `PASS_PARTIAL_INSTALLED_COMPONENTS_SPDX_LIMITED`; se recibió y verificó directamente el SPDX real. Expediente **documental liviano** formado y aceptado expresamente por el owner. **Rama documental limitada cerrada.** | SBOM **no exhaustivo**; R2 **sin OCI/TAR portable ni importación en host independiente**, assets offline Tectonic no acreditados. **F3 pleno del plan: no acreditado**. |

**Interpretación:** se cierra **I0-1F en alcance técnico-documental acotado, con reservas explícitas**, por decisión humana y evidencia delimitada. Se **preservan como objetivos no demostrados**, sin reclasificarlos como PASS, las propiedades requeridas para un **cierre pleno** de F2/F3. No se abre una F4 ni una nueva campaña para obtener un rótulo de cierre.

## 3. Evidencia F3 incorporada y verificación directa

**Expediente único de F3:** `I0-1F_F3_ENTREGA_DOCUMENTAL_LIMITADA_H_R2.zip` — **18.710 bytes**, SHA-256 comprobado `4b2e1e64c70c27293559ed205b833448afa2ee098a127f17df307c5471458769`. Se comprobaron el CRC del ZIP y los hashes de sus **5/5 miembros inventariados** en `SHA256SUMS.txt`; el manifiesto no se incluye a sí mismo. Contiene SPDX original, catálogo histórico H de F2, registro de procedencia, manifiesto, README y acta F3 anterior a la aceptación.

**SPDX 2.3 original** `I0-1F_F3_R2_INSTALLED_COMPONENTS_LIMITED.spdx.json`: **155.270 bytes**, SHA-256 verificado `a09cf3b7e4255dac573a1d2296723230441f8ae7ef6d1cd6ee076b8df111a4ff`, sin reserialización. La inspección directa acotada constató `SPDX-2.3`, documento y raíz H referenciada, **269 paquetes** (1 raíz, **162 registros** de metadatos Python, **106 dpkg**), **270 relaciones**, **271 SPDXIDs únicos**, referencias sin romper y un archivo Tectonic `/usr/local/bin/tectonic` con SHA-256 `f0b36e78c13dd75b821984830533f872c9a12c62957e51357bc16e65cdb71013`. El caso de igual nombre/versión Python con **dos orígenes de metadatos** fue conservado explícitamente; no se infieren instalaciones independientes solo por esa diferencia.

**Clasificación:** `PASS_STRUCTURAL_SPDX_LIMITED` sobre bytes recibidos, **no** certificación formal integral SPDX, inventario de filesystem/capas, análisis completo de licencias, vulnerabilidades o transitivas OS. `NOASSERTION` en licencias no equivale a licencia verificada. La detección focalizada sin indicadores de secretos no asegura su ausencia absoluta.

**Procedencia separada:** la ejecución real F3-S03 R2 (contenedor efímero sin red, rootfs RO, sin mounts, sin build/pull/export) y sus conteos provienen del **registro de consola del operador**; la integridad y la estructura del archivo anexado se verificaron aquí **directamente sobre sus bytes**. El archivo original y el instrumento R2 mantienen sus hashes/identidades; no fueron reejecutados.

**Incidentes conservados:** F3-S02 Docker Scout terminó por límite instrumental de lectura/descompresión y dejó un temporal que se recuperó con autorización dirigida; **no** demuestra corrupción de H. F3-S03 R1 rechazó una clave de identidad de duplicados insuficiente y **no** produjo SPDX; el ajuste R2 produjo el inventario parcial válido. Ningún STOP o REVIEW histórico se borra o convierte retrospectivamente en PASS.

## 4. Reservas y no conformidades que sobreviven al cierre

| Dimensión | Estado final honesto |
|---|---|
| Dos reconstrucciones independientes de C | `NOT_RUN`; reproducibilidad bitwise `NOT_DEMONSTRATED`. |
| Exportación de R2, verificación de importación aislada y ejecución en segundo host | `NOT_PERFORMED` / **`F3_FULL_PORTABILITY: NOT_ACCREDITED`**. Un catálogo o ZIP de documentos no es una imagen portable. |
| Recursos Tectonic/tlextras completos fuera del host histórico | Portabilidad offline funcional `NOT_DEMONSTRATED`; identidad del ejecutable no acredita todos sus assets. |
| SBOM de todas las capas/archivos, licencias, CVEs y origen externo autenticado | **`F3_EXHAUSTIVE_SBOM: NOT_DEMONSTRATED`**; no firma/SLSA/upstream autenticado. |
| Fidelidad STEM | **`E2-02_MATH_PRESERVATION_FAIL_OBSERVED`**: pérdida visible de notación en ecuaciones **(1.1)–(1.4)** y degradación de layout del PDF R2 con fake LLM; **causa y solución no acreditadas**. |
| Funcionalidad de producto | I0-1D acredita un PDF→PDF local con proveedor sintético, 5/5 tareas y 61 proyecciones; no traductor con Groq real ni calidad lingüística/científica validada. I0-1E conserva sus 2 warnings E3 no clasificados y límites de aislamiento/CI. |
| Aprobación normativa / producción | Atlas §9 `IN_PROGRESS`; Charter §6 y contrato D1 `DRAFT`. No aprobación del Board, selección canónica, certificación de seguridad universal ni autorización de despliegue productivo. |

**No conformidad E2-02:** se hereda **íntegra**, sin reabrirla en I0-1F ni declarar corrección. Los cierres previamente aceptados de I0-1D e I0-1E conservan exactamente sus alcances y advertencias.

## 5. Registro de decisión humana, límites de autoridad y publicación

**Secuencia de decisión:** (a) el owner aprobó el plan rector F0→F3; (b) decidió explícitamente priorizar `REUSE FIRST` y no duplicar imágenes pesadas; (c) luego de recibir el expediente F3 y el dictamen de límites, **respondió afirmativamente a la solicitud de aceptación del cierre documental limitado F3**; (d) seguidamente **solicitó emitir directamente una única acta consolidada final I0-1F** para evitar nueva burocracia documental. Estos actos autorizan **este cierre técnico-documental acotado**; no autorizan tareas adicionales con efectos laterales ni certifican las propiedades pendientes.

El expediente F3 anterior conserva, **como fotografía del momento en que fue escrito**, las leyendas `PENDIENTE_ACEPTACION_OWNER` y `READY_FOR_OWNER_ACCEPTANCE`. **Este acto posterior registra la aceptación del owner sin reescribir ni sobrescribir aquella evidencia**. Tampoco constituye una firma digital o un commit. La emisión de esta acta, por sí sola, **no prueba recepción, revisión de cada línea o firma del archivo final por el owner**.

**Dictamen consolidado:** `I0-1F_CERRADO_TECNICAMENTE_EN_ALCANCE_DOCUMENTAL_LIMITADO_CON_RESERVAS`. No se declara `I0-1F_FULL_PASS`, `BUILD_REPRODUCIBLE`, `IMAGE_PORTABLE`, `SBOM_EXHAUSTIVE` ni `PRODUCTION_READY`.

**Efectos realizados al preparar esta acta:** lectura de fuentes documentales adjuntas y consulta **solo lectura** del estilo documental en la ruta indicada del repositorio. **Sin** Docker, Scout, build, pull, exportación, limpieza, instalación, escritura en Git, alteración del checkout, Atlas, Charter, corpus, oráculos, contenedores, volúmenes o custodia histórica. La publicación del Markdown en el repositorio requiere una decisión y una operación Git separadas, protegiendo las modificaciones editoriales locales ya existentes.

**Continuidad:** I0-1F queda documentada en el alcance aceptado. Cualquier necesidad futura de distribución real, cold builds reproducibles o certificación científica exigirá objetivos, criterios y autorizaciones propios; **no se inicia ni prescribe esa ejecución mediante este cierre**.

## 6. Fuentes y cadena de referencia (sin duplicar expedientes)

1. **Gobierno y forma:** `PROJECT_SCOPE.md`, `ENGINEERING_PRINCIPLES.md`; repositorio `docs/architecture/adr/pipeline-stabilization/00-foundation/I0-1C_ACTA_CIERRE_TECNICO_ACEPTADA_2026-10-22.md`, `PRODUCTION_PIPELINE_EXECUTION_ATLAS.md`, `PIPELINE_STABILIZATION_AUDIT_CHARTER.md`, `L0_D1_REPRODUCIBLE_BUILD_AND_AUDIT_HARNESS_CONTRACT_DRAFT.md` (sus estados normativos no se alteran).
2. **Cierres precedentes aceptados:** `I0-1D_ACTA_CIERRE_TECNICO_ACOTADO_ACEPTADA_2026-10-31.md`; `I0-1E_ACTA_CIERRE_TECNICO_ACOTADO_ACEPTADA_20261101.md`; hallazgo `I0-1E_E2_02_ACTA_COMPARACION_DOCUMENTAL_R2_20261101.md`.
3. **Plan y F1:** `I0-1F_PLAN_RECTOR_EJECUCION_SOTA_ACOTADO_v0.1_20261101.md`; `I0-1F_F1_ACTA_CIERRE_TECNICO_ESTATICO_Y_TRANSICION_F2_PREFLIGHT_20261102.md`; `I0-1F_F1_CONSOLIDACION_MATERIALES_Y_DECISION_F2_NO_GO_20261102.md`.
4. **F2:** `ACTA_F2_REUSE_FIRST_Y_F3.md`; `I0-1F_F2_ADENDA_REUSE_FIRST_Y_ENTREGA_H_PROPUESTA_20261102.md`; catálogo `H_CATALOGO_R1.json`; expediente precursor F2 inalterado.
5. **F3:** salida histórica `F3-S03 R2` del operador reproducida en el prompt maestro de traspaso; `I0-1F_F3_S03_ADENDA_DUPLICADOS_R2_20261102.md`; expediente **`I0-1F_F3_ENTREGA_DOCUMENTAL_LIMITADA_H_R2.zip`**, incluido su SPDX original y `SHA256SUMS.txt`.

**Regla de precedencia:** pruebas primarias y hashes de archivos realmente recibidos > salidas del operador en su alcance declarado > actas históricas > propuestas y snapshots documentales anteriores. La aceptación humana **posterior** actualiza el *estado de decisión*, no los bytes de la evidencia histórica.

**Fin del acta — I0-1F, cierre técnico-documental acotado con reservas, 2026-11-02.**
