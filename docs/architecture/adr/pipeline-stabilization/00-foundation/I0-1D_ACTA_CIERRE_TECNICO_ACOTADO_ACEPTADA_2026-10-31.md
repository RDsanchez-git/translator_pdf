# I0-1D — Acta técnica de cierre de instalación aislada y construcción del producto

**Fecha de decisión del operador:** 2026-10-31 (corte local informado).  
**Estado:** `CIERRE TÉCNICO I0-1D ACEPTADO POR EL OPERADOR — EN ALCANCE ACOTADO; PUBLICACIÓN GIT PENDIENTE`.  
**Dictamen aceptado:** `I0-1D_CERRADO_EN_ALCANCE_ACOTADO_CON_RESERVAS`.  
**Gate final adjudicado:** `D2-12_R2_INCREMENTAL_BUILD_AND_FAKE_PDF2PDF_EVIDENCE_PASS_LIMITED`.  
**Acreditación:** instalación offline histórica y construcción incremental **local** de R2, con dependencias y caches externas identificadas; **NO_ACREDITADA_PRODUCCIÓN**.  
**Repositorio:** `RDsanchez-git/translator_pdf` · **rama:** `pipeline_stabilization` · **HEAD integrado ejecutado:** `d4cda2c379c0efd93a70e795d31c37a0ede7a192`.  
**Publicación:** este documento se entrega para la ruta `docs/architecture/adr/pipeline-stabilization/00-foundation/`; **no se ha efectuado commit, push ni edición del Atlas por la emisión de esta acta**.

## 1. Decisión, autoridad y frontera de fase

El operador solicitó expresamente concluir I0-1D, después de que se le explicaran dos modalidades, y eligió continuar con el **cierre incremental acotado (Vía A)**. Su aceptación se refiere al artefacto Docker local identificado, derivado de la imagen histórica fijada, y a los resultados instrumentales y funcionales concretos de D2-12. La emisión de esta acta no supone firma digital, auditoría externa, promoción a producción ni aprobación de una ruta canónica de arquitectura.

**Objeto de I0-1D:** demostrar instalación aislada de las dependencias y construcción de un entorno final de ejecución con identidad verificable. La validación funcional integral, E2E, seguridad, PDF mínimo y análisis de estructura corresponden a **I0-1E**; el SBOM, la procedencia final, la reproducción portable y el archivo criptográfico integral a **I0-1F**. Las pruebas funcionales ejecutadas aquí son **evidencia adicional y acotada de aceptación del artefacto**, no el cierre anticipado de I0-1E.

Se distinguen tres sujetos: (a) **fuente I0-1 congelada** `c56f3e124d76ae9f1506e4b12fbf0faa4881b574`, cuyos pilotos D2-10/R1 continúan en STOP; (b) imagen D1 original `sha256:95300da97b595195d67e94d20673815643ee60bfd93eb658b894418871b5036c`; y (c) **producto R2 derivado del HEAD integrado** `d4cda2c…`, que constituye el artefacto aceptado en este cierre. Los PASS de (c) no alteran los STOP de (a).

## 2. Evidencia histórica de materiales, instalación y construcción

| Control | Resultado atribuido y límite |
|---|---|
| I0-1C y D0 | Lock fijado, **158 wheels**, contexto D0-15C de 493 archivos, materiales `APPROVED_MATERIALS` aprobados **para el gate estático**; no certificación final. |
| D1-01 | Build histórico de producto **exit 0**, instalación `pip` offline con `--no-index` y `--require-hashes`, binario Tectonic incluido y prefijo de seis capas base verificado. |
| D1-02A/B | Imagen histórica inspeccionada y **13/13 controles de entorno PASS_LIMITED**; Python, Tectonic/ELF, dependencias y bibliotecas principales. |
| D2-10/R1 | **STOP preservados** en el sujeto original: primero caché BPE ausente; después `ATTACH fsm_db` duplicado y durabilidad FSM no acreditada. No hubo PDF final en esas ejecuciones. |
| D2-11 | **Cierre documental acotado aceptado**, con W04/R3, W06/R1 y W07/cache abiertos. No hubo designación de R2 como ruta canónica. |

La copia íntegra de los 158 wheels permanece bajo `I0-1D_D0_15C_ASSEMBLY_01/context/wheels`. Los 158 wheels duplicados de D0-13 se retiraron **tras comparación 158/158 por SHA-256 y autorización específica**, conservando los manifiestos y expedientes históricos. Su eliminación no constituye pérdida del único wheelhouse ni modifica el resultado de D0-14.

## 3. D2-12 — Construcción incremental del HEAD integrado

| Propiedad | Evidencia del operador |
|---|---|
| HEAD Git del producto | `d4cda2c379c0efd93a70e795d31c37a0ede7a192` |
| Imagen padre preinstalada | `g3-b4-10/translator-pdf-runtime:fbf166b-derived-r0` |
| ID del padre | `sha256:b476a8ceedb67a6843bb8673ba9defd87d939d18d09066b0b428882960a0e302` |
| Imagen final R2 | `i0-1d/translator-pdf-runtime:r2-d4cda2c-20261031_211824` |
| ID de R2 | `sha256:abe5b5dbbc65e8920e0948b189bd9bd090eb395e99420918190128a2ec12b4bd` |
| Arquitectura/usuario | `linux/amd64`, UID/GID `10001:10001`, directorio `/app` |
| Build incremental | **16/16 pasos, exit 0, ~2,3 s**, contexto ~1,20 MB, sin reinstalación `pip`, sin `pull` declarado |
| Relación de capas | Padre 25, R2 35; **prefijo del padre 25/25 PASS** |
| Fuente exportada desde Git | **346/346 hashes SHA-256 PASS**, cero archivos extra en los árboles cotejados; módulos anteriores reubicados ausentes |

**Método preciso:** la nueva imagen sustituyó seis directorios de aplicación y `pyproject.toml` a partir de una exportación limpia `git archive` del HEAD. El padre, que ya contenía instalación Python y Tectonic, fue reutilizado **por su identidad local**. El Dockerfile de actualización eliminó árboles antiguos de la vista de archivos mediante una capa (whiteouts); **esto no elimina los bytes originales de las capas del padre**. No se ejecutó reconstrucción fría desde la OCI nativa en un daemon vacío, ni se exportó un TAR portable de la nueva imagen.

**Testigos primarios del build:** directorio de custodia `I0-1D_D2_12_R2_INCREMENTAL_20261031_211824/`: `HEAD_SOURCE.zip`, `SOURCE_SHA256.csv`, `BUILD_PROVENANCE.json`, `context/Dockerfile.r2`, `RESULTADO.txt` y registros de verificación. Las identidades de imagen y los SHA de cada fuente fueron comprobados en la máquina del operador; **no se inventan SHA literales de archivos no transcritos en la conversación**.

## 4. Comprobaciones del runtime R2 y aceptación física de alcance limitado

| Comprobación | Resultado observado |
|---|---|
| Compatibilidad sin red, rootfs RO, UID 10001 | Python **3.11.17**, **327** módulos sintácticamente válidos, Tectonic ejecutable, `pip check`: `No broken requirements found.`; `exit 0`. |
| Importaciones de módulos seleccionados | **10/10 PASS**, cero fallos, origen `/app`, `docker run exit 0`. Sonda SHA-256 `B5004FCC82230DF828CCA13C4A40760D7BF79BA4888AE4A4158DD5D96D808B98`. |
| SQLite WAL / expiración / fencing aislado | **2/2 PASS** en el alcance del repositorio de leases; `exit 0`. No se arrancó un reconciliador daemon completo en esta sonda. |
| PDF→PDF integrado con fake LLM | **5 tareas COMPLETED**, cinco recibos, **61 proyecciones**, FSM `COMPLETED`, errores/reintentos observados: 0/0. |
| Archivo físico | `PDF_FINAL_R2.pdf`: **20.902 bytes, cuatro páginas reportadas**, SHA-256 cotejado con `FINAL_RESULT.json` y `FINAL_RECEIPT.json`: **PASS**. |
| Estado SQLite | **Seis backups online individuales** (`documents`, `event`, `fsm`, `materialized`, `queue`, `rate_limits`), SHA-256 y tamaño cotejados, `integrity_check=ok` reportado para cada uno. |
| Salida del laboratorio | `R2_FINAL_STATUS: PASS`, `EJECUTOR_EXIT: 0`; servicios detenidos controladamente y objetos de laboratorio preservados. |

**Expediente del laboratorio PDF→PDF:** `I0-1D_D2_12_R2_PDF_A_PDF_r2d12d4cda2c01_20261031_222214/`, con `RUN_STATUS.txt`, `FINAL_RESULT.json`, `FINAL_RECEIPT.json`, `PDF_FINAL_R2.pdf`, `SQLITE_BACKUP_REPORT.json`, `SQLITE_ONLINE_BACKUPS/` y logs. El operador ejecutó adicionalmente un cotejo de solo lectura de los archivos exportados: `AUDITORIA_ARCHIVOS_EXPORTADOS_R2: PASS`, incluido PDF y **6/6** backups. Es **evidencia de la ejecución en su host** comunicada en la conversación, no una segunda lectura independiente de C: por el redactor.

**Límite de la prueba:** proveedor simulado, caché BPE y recursos TeX externos sembrados desde paquete histórico G4 b03; **no hubo traducción real mediante Groq**. Los seis backups son consistentes individualmente, **no** una única transacción atómica sobre seis bases. Esta ejecución no certifica aislamiento de egreso global ni cobertura de documentos arbitrarios.

## 5. STOP del finalizador documental R1: no imputable al producto

El intento posterior de generar un acta con `CIERRE_I0_1D_ACOTADO_R1.py --check` terminó en `I0_1D_CIERRE_STOP: Stop IMPORT_LOG_INCOMPLETO` y **no emitió un acta aceptada**. Este STOP se preserva. Es una **incidencia de lectura/validación documental**, no un fallo nuevo del build, las importaciones o PDF→PDF. El verificador leía `R2_IMPORT_STDOUT_COMPLETO_20261031_215249.txt` con `utf-8-sig`, aunque `Tee-Object` en Windows PowerShell 5.1 suele escribir UTF-16LE; esta **hipótesis de causa instrumental** es consistente con un rechazo de coincidencias de texto, pero no se ha comprobado directamente la codificación de los bytes Windows.

Existe un testigo más apropiado y ya emitido: `R2_IMPORT_CAPTURA_ESTADO_20261031_215249.txt` declara `DOCKER_EXIT=0`, `IMPORTACIONES_PASS=10`, `IMPORTACIONES_FAIL=0`, `MARCADOR_PASS=1`, `RESULTADO_CAPTURA=True`, y la salida íntegra de la sonda fue facilitada con diez líneas `PASS`, `R2_IMPORT_SMOKE: PASS`. **Esta acta no convierte el STOP del finalizador en PASS ni reejecuta la prueba**: distingue el cierre técnico aceptado sobre evidencias anteriores de una automatización documental adicional fallida.

## 6. Reservas explícitas y responsabilidades de I0-1E / I0-1F

- **Reproducibilidad:** el cierre acepta **build incremental local con padre identificado**. No está probado el build portátil desde un daemon/almacén vacío ni la disponibilidad transportable de todas las capas e insumos necesarios. El archivo final y SBOM son asuntos de I0-1F.
- **Cachés y custodia:** el PDF→PDF requirió recursos BPE/Tectonic aportados externamente. Los dos archivos históricos `tlextras-2022.0r0.tar` y `.zip` fueron movidos a Google Drive y **carecen de comprobación remota de SHA-256**; esto permanece pendiente de custodia, sin invalidar retrospectivamente el build observado.
- **Validación y seguridad:** egress cero global independiente, pruebas E2E y regresión científica completa, interpretación de PDF STEM/escaneados, calidad lingüística real, rendimiento y seguridad operativa siguen pendientes de sus fases/autoridades correspondientes. El CI científico histórico reportó falta de 15 PDFs de baseline; no fabricar resultado PASS.
- **Rutas y resiliencia:** W04/R3, W06/R1, W07/caché relativa, política `FAILED_RETRYABLE` y ventana de crash entre promoción de archivo PDF y commits SQLite permanecen abiertas. Las dos pruebas SIGKILL de G5/2 corresponden a otro sujeto/revisión y **no se repiten ni atribuyen a R2 integrado**.
- **Procedencia:** SHA-256 demuestra integridad respecto de anclas, no autenticidad independiente de editor/publicador. No se declara firma digital de esta acta ni certificación de producto.

## 7. Dictamen técnico aceptado y publicación pendiente

**Dictamen de cierre técnico:** `I0-1D_CERRADO_EN_ALCANCE_ACOTADO_CON_RESERVAS`. Se consideran atendidos **dentro de la Vía A aceptada** los objetivos de instalación aislada histórica, construcción de un producto R2 integrado identificable y comprobación básica de ejecución con dependencias ya instaladas. El PASS físico PDF→PDF constituye evidencia adicional de que la imagen es funcional bajo las condiciones indicadas. El D2-12 se adjudica `PASS_LIMITED` sin extender ese resultado a I0-1E ni I0-1F.

**Aceptación humana:** solicitud expresa del operador de terminar I0-1D mediante cierre acotado y de elaborar un acta análoga a I0-1C, comunicada en esta conversación. **Sin firma digital o autógrafa.** No se declara aprobado el finalizador R1 fallido.

**Estado de la publicación:** `PENDIENTE`. Esta copia Markdown se ofrece para incorporación controlada al repositorio. No se realizó `git add`, `git commit`, `git push`, PR ni merge. No se modificó `PRODUCTION_PIPELINE_EXECUTION_ATLAS.md`, ni se borraron expedientes/volúmenes ni se normalizaron STOP históricos.

## 8. Custodia y continuidad

**Registro acumulativo de referencia:** `I0-1D_REGISTRO_HISTORICO_TECNICO_VIVO_v0.19.0_PROPUESTA_D2_12_Y_PRECIERRE_20261031.md`, SHA-256 de esta copia propuesta `cc59ad17d77b249002f71e3f77604403e573949c804ddb95207ad2ddc0aa26ad`. Conserva las Partes A/B/C y sus cortes históricos. El acta **añade una adjudicación posterior**, sin retroeditarlo. Su incorporación al repositorio será una operación editorial separada.

**Custodia externa primaria:** `C:\Users\Admin\Desktop\Proyectos\I0-1_ARCHIVO_AUDITORIA`. Las rutas de evidencia se interpretan respecto de dicha raíz; no se deben versionar wheels, datos privados, TAR de imágenes, credenciales, SQLite, PDFs de laboratorio ni cachés de Tectonic como parte del acta.

**Transición:** I0-1D **cerrado técnicamente en alcance acotado**, I0-1E **pendiente de apertura formal y de sus gates propios**, I0-1F **pendiente de I0-1E**. El acta de I0-1C y el registro de I0-1D son referencias cruzadas; **la publicación Git no es la condición que define la aceptación técnica local**.
