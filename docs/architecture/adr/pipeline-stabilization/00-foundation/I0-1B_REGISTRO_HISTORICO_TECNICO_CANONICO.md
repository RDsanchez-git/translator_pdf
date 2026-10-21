# I0-1B — Registro histórico técnico canónico

**Proyecto:** `translator_pdf` · auditoría I0-1 de suministro, reproducción y aislamiento  
**Edición:** `v1.1 — integración documental en Pipeline Stabilization` · **fecha:** 2026-10-21  
**Naturaleza:** memoria operativa y de decisiones, **no certificado independiente ni reemplazo de evidencia primaria**.  
**Estado:** consolidación A+B+G5-B histórico, revisada editorialmente para su incorporación a `00-foundation`; **pendiente de aceptación/commit del operador**. No es certificación integral de I0-1A–F ni auditoría independiente del host; las salvedades del §10 siguen explícitas.  
**Regla:** ante contradicción, prevalece el registro original de ejecución verificable; este documento se corrige por versión, **nunca reescribiendo los expedientes**.

### Ubicación, autoridad y relación con la auditoría PDF → PDF

- **Ubicación documental propuesta:** `docs/architecture/adr/pipeline-stabilization/00-foundation/I0-1B_REGISTRO_HISTORICO_TECNICO_CANONICO.md`, en la rama `pipeline_stabilization` de `RDsanchez-git/translator_pdf`. Este registro es una **memoria histórica auxiliar de evidencias instrumentales**, no un ADR aprobado, un HITO forense cerrado del Atlas, un gate normativo ni un cambio del producto.
- **Atlas rector de la investigación:** [PRODUCTION_PIPELINE_EXECUTION_ATLAS.md](./PRODUCTION_PIPELINE_EXECUTION_ATLAS.md), v0.2.15, estado `IN_PROGRESS`, especialmente §9 (L0/preflight, L1/E2E-0, L2/testigos y L3/cierre diferido). I0-1B demuestra resultados **instrumentales acotados** de adquisición y consumo OCI local; **no** acredita los checkpoints L1 ni el PDF→PDF E2E del producto.
- **Prerregistro / autoridad:** [PIPELINE_STABILIZATION_AUDIT_CHARTER.md](./PIPELINE_STABILIZATION_AUDIT_CHARTER.md), v0.1.0 `DRAFT`, y metodología forense aplicable en su propio alcance. Este registro **no aprueba** D-1…D-7, no asigna un HITO formal, no cambia criterios ni promueve evidencia a `FROZEN`/certificación.
- **Documentos de ejecución subordinados relacionados:** [E2E_0_PREFLIGHT_AND_EVIDENCE_PLAN_DRAFT.md](./E2E_0_PREFLIGHT_AND_EVIDENCE_PLAN_DRAFT.md), [L0_AUDIT_SANDBOX_DESIGN_AND_VERIFICATION_SPEC_DRAFT.md](./L0_AUDIT_SANDBOX_DESIGN_AND_VERIFICATION_SPEC_DRAFT.md), [L0_D1_REPRODUCIBLE_BUILD_AND_AUDIT_HARNESS_CONTRACT_DRAFT.md](./L0_D1_REPRODUCIBLE_BUILD_AND_AUDIT_HARNESS_CONTRACT_DRAFT.md) y [L0_PF08_PF09_ISOLATION_EGRESS_REVIEW_DRAFT.md](./L0_PF08_PF09_ISOLATION_EGRESS_REVIEW_DRAFT.md). Mantienen su estado `DRAFT` y su corte documental histórico; los testigos de imagen nativa no sustituyen el build del producto, la verificación del sandbox ni una corrida E2E.
- **Identidades distintas, no intercambiables:** el sujeto fuente I0-1 congelado en `c56f3e124d76ae9f1506e4b12fbf0faa4881b574` no es el baseline `95ef8a38614a1416484593fbd734443e57a74369` declarado por el Atlas. La publicación de este documento en una rama posterior tampoco cambia el commit, la configuración ni la identidad de los sujetos ensayados. El expediente primario está **fuera del repositorio**; las rutas del §12 son localizadores históricos y no garantizan disponibilidad pública de esos artefactos.
- **Frontera de continuidad:** pasar a diseñar I0-1C requiere una decisión/permiso independiente de adquisición y comprobaciones de elegibilidad propias. No implica autorizar tráfico hacia PyPI ni ejecutar `uv`, Docker Compose, CLI del traductor o el sandbox.

### Cambios de v1.0 a v1.1 — ubicación e integración documental (sin ensayos nuevos)

- Se adaptó exclusivamente la cabecera editorial a la estructura `00-foundation`, identificando Atlas, Charter, planes L0/E2E y contrato de build como documentos relacionados.
- Se distinguió el commit del sujeto I0-1 de la baseline del Atlas, y el éxito funcional de imagen OCI local de un ensayo E2E o de certificación de aislamiento.
- **No** cambian los resultados, los expedientes primarios, las fuentes E01–E25 ni las salvedades de v1.0. Hash de v1.0 anterior a esta revisión: `1de429af6e895866a2d861709d31907f1ddab6debfb6bb5fcb1afe9e7a39dd93` (SHA-256 del archivo Markdown de origen).

> **Leer primero (90 segundos).** La fuente I0-1 fue congelada en el commit `c56f3e124d76ae9f1506e4b12fbf0faa4881b574` (328 archivos; 24 dependencias directas). Se adquirió/verificó el bundle TeX histórico; Tectonic 0.15.0 pasó una prueba de enlazador y generó un **PDF mínimo** sin red de aplicación en un ensayo acotado. Se construyó y congeló una base nativa Graphite2. La cadena OCI del TAR se verificó localmente. La resolución literal offline `FROM i0-1b/native-base@sha256:5de4...` **no** funcionó: BuildKit intentó consultar metadatos de Docker Hub. El contrato alternativo `--build-context frozen_oci=oci-layout://...` **sí** produjo en G5-B local OCI v2 un build con código `0` y un testigo `os-release` idéntico en bytes al congelado. El gate v2 **no** imprimió PASS: terminó en STOP por un filtro textual de `docker.io/` que disparó sobre una línea de progreso del contexto local. No se demostró la inexistencia global de tráfico de red, ni un build del producto, ni E2E. `uv` 0.12.20 **sí fue observado posteriormente** mediante `--version` y ayudas en G5-A-X; **no** se ejecutó `uv pip compile` ni se adquirieron wheels. I0-1C es la siguiente fase de diseño/autorización, no una descarga ya permitida. **En B** se ratificaron directamente ambos testigos G5-B, el PDF mínimo y el resultado final de `uv` tras restaurar Wi-Fi; este documento sigue sin certificar egress global, export único ni I0-1A/E2E.

### Cambios de v0.1 a v1.0 — conciliación B e histórico

- **G5-B:** se verificaron directamente los 267 bytes de cada testigo, su igualdad exacta y ambos hashes contra el manifiesto original de expediente, sin ejecutar Docker [E18]. Se preserva el STOP del gate y la salvedad del export completo.
- **uv:** G5-A-X tiene JSON **final** `VERSION_AND_HELP_PASS_AFTER_WIFI_RESTORE_ONLY` y `wifi_restored=true`; G5-T permanece `NOT_ACCEPTED_NO_RETRY` [E19,E23].
- **Tectonic:** PDF mínimo real de **4.263 bytes** y SHA-256 del manifiesto G4-X cotejado; esto **no** prueba el traductor de punta a punta [E20].
- **Cadena TeX y base nativa:** se añadieron G1–G3, log de build 03 y metadata Docker; se delimita que no se rehasharon TAR/ZIP voluminosos originales [E21,E22,E25].
- **Custodia:** comprobados los 160 elementos A, los 26 B y los 10 del expediente retrospectivo secundario H; A+B reúnen **186 copias de 180 rutas distintas** (seis manifiestos duplicados, todos idénticos por SHA-256). Solo A+B son copias documentales del host. El documento queda listo **para revisión del operador**, no publicado en Git automáticamente.

## 1. Cómo usar este documento sin perder rigor

1. **Consultar primero el estado actual** (§2), las prohibiciones (§3), el hito relevante (§5–§8) y el protocolo de continuidad (§11).
2. **Buscar después el registro primario** mediante los IDs de fuentes del §12. Las referencias son rutas relativas a `C:\Users\Admin\Desktop\Proyectos\` (raíz histórica del operador), no enlaces garantizados en otro equipo.
3. **Separar cuatro planos de evidencia:** `P` = archivo primario/resultado disponible en las recopilaciones A o B (copiado y hash verificado en el paquete, con chequeo cruzado de manifiesto de origen cuando se declara); `A` = acta que reproduce o interpreta salidas del operador; `C` = consola aportada en la conversación, contrastada cuando se indica; `H` = síntesis histórica secundaria de G5-B; `D` = diseño, prueba sintética o propuesta sin ejecución real. Una copia con hash no prueba por sí sola origen, autor, ausencia de manipulación previa ni integridad del host.
4. **No inferir un éxito más amplio a partir de un PASS estrecho.** Una prueba de loader no es un PDF; un PDF mínimo no es E2E; un testigo OCI no es build del traductor; una ayuda de `uv` no es resolución de dependencias.
5. **No borrar ni reabrir un STOP.** El STOP de G5-T, el de `FROM` literal y el del gate local OCI v2 conservan su valor histórico. Una evaluación funcional retrospectiva se anota como observación independiente, no como alteración del veredicto original.
6. **No atribuir cronología únicamente al mtime.** Varios archivos presentan fechas normalizadas a medianoche. Preferir IDs UTC de expediente, `start_utc.txt`, `finish_utc.txt`, transcripciones/actas y orden causal. Los registros antiguos redactados después de una ejecución no se convierten en evidencia simultánea.

## 2. Matriz de estado — al 21 de octubre de 2026

| Hito / contrato | Lo que está respaldado | Lo que NO está demostrado / cierre |
|---|---|---|
| **I0-1A, fuente** | Snapshot aislado: commit, tree, manifiesto de 328 archivos; el `pyproject.toml` copiado contiene 24 dependencias runtime. Evidencia documental de preservación y controles de atlas. | El rótulo global «I0-1A COMPLETADO» de la hoja de ruta del chat aún requiere conciliación contra todas las fuentes I0-1A; no asumir que valida el producto. |
| **TeX G0/G1/G2** | Adquisición TAR histórico; G2 comunica verificación de 134.980 entradas, 134.979 contenidos y hashes físico/lógico. | No hay firma independiente del publicador; algunos cierres se basan en transcripción del operador, no en captura firmada. |
| **TeX G3** | Derivación ZIP64 local y revalidación de equivalencia de contenido: `G3_ZIP_CONTENT_EQUIVALENCE_PASS_STATIC_ONLY` según acta. | No es prueba de compilación; esta llegó después, en G4. |
| **Tectonic loader** | Enlazador ELF resolvió bibliotecas de Tectonic 0.15.0 dentro de base Graphite2: `TECTONIC_MINIMAL_DYNAMIC_LOADER_PASS`. | No es ejecución normal de Tectonic ni certificación upstream. |
| **Tectonic G4-X** | **PDF mínimo** (4.263 bytes reportados), Tectonic exit `0`, ZIP local, `--network none`, cierre `G4_X_OFFLINE_TECTONIC_MINIMAL_PDF_PASS`. | PDF físico de 4.263 bytes incluido y SHA-256 cotejado con el manifiesto original en B. La prueba G4-X solo verificó cabecera/tráiler; no demuestra estructura PDF integral, fuentes embebidas ni producto E2E. |
| **Base nativa** | Build 03 terminó `0`; imagen de 6 capas, TAR exportado y hash congelado; Graphite2. | No equivale a construir la imagen final ni a instalar paquetes Python. |
| **uv G5-T** | Registro histórico `G5_T_NOT_ACCEPTED_NO_RETRY`, por detección incorrecta de `--constraint` singular frente a `--constraints` plural. | No se puede promocionar ese ensayo a PASS. |
| **uv G5-A-X posterior** | Versión `uv 0.12.20`, ayudas y resultado JSON **`VERSION_AND_HELP_PASS_AFTER_WIFI_RESTORE_ONLY`**; `docker_exit_code=0` y `wifi_restored=true`, comprobados en la recopilación B. | No se probaron combinaciones de CLI, resolver, índices, lock, wheelhouse ni restauración completa en el extracto de transcripción seleccionado. |
| **OCI/G5-B vínculo TAR** | Índice `5de4...`, manifiesto amd64 `1b530...`, configuración `b9b8...`, seis capas y testigo local documentados. | Identidad OCI no prueba disponibilidad externa de registro, firma de origen o resolución offline de `FROM`. |
| **G5-B `FROM` literal** | Buildx/BuildKit intenta `HEAD` al registro remoto y falla por DNS offline; **no** hay build exitoso. | Contrato literal **NO aprobado**. `--pull=false` y `--network none` no impiden necesariamente la resolución de metadatos de fuente. |
| **G5-B OCI contexto local** | v2 `build_exit_code=0`, progreso `OCI load from client`, `COPY` y export; en B se leyeron directamente ambos testigos de 267 B: bytes idénticos y hashes iguales al manifiesto original; 14 archivos de workcopy intactos según gate; inventarios estables. | Veredicto del **gate v2: STOP** por regex de log; sin certificación global de egress y sin prueba equivalente del contrato literal. |
| **I0-1C** | Decisiones para planificación: PyPI único, corte UTC fijo, wheels únicamente; diseños de controles. | **No iniciada operativamente:** sin `requirements.lock` aprobado, sin wheelhouse, sin descargas autorizadas. |
| **I0-1D/E/F** | Etapas definidas en hoja de ruta I0-1. | Instalación offline, build final, sandbox/CLI del producto, HV/E2E, SBOM/atestaciones y certificación final **pendientes**. |

**Dictamen agregado permitido:** «infraestructura/base y demostraciones funcionales **acotadas**; contrato alternativo de consumo OCI local exitoso a nivel testigo; cadena de certificación I0-1 general abierta». No usar «I0-1B 100% air-gapped certificado» ni «producto auditado».

## 3. Identidades congeladas, fronteras y prohibiciones

### 3.1 Fuente / sujeto

- Repositorio **fuera de alcance de escritura** durante estos ensayos: `C:\Users\Admin\Desktop\Proyectos\translator_pdf`; rama histórica `pipeline_stabilization`.
- Commit sujeto `c56f3e124d76ae9f1506e4b12fbf0faa4881b574`; tree `eb7d2f6770517b72546055f4b611bac4734a3db3`.
- Snapshot externo `i0-1-source` con `metadata/source_manifest.json` (328 archivos, según manifiesto) y `src/pyproject.toml` (24 dependencias en `[project].dependencies`). La comparación con el working tree actual del repositorio debe respetar la excepción documentada del atlas, no asumir que Git está limpio sin inspección.
- En G5-R, el pin `groq==1.4.0` se describe como **restricción instrumental**, no como reconstrucción probada de una dependencia histórica del usuario.

### 3.2 Imágenes y artefactos nativos

- Base inicial local: `python:3.11.17-slim-bookworm` para `linux/amd64`; runtime documentado Python `3.11.17`, glibc `2.36`, SOABI `cpython-311-x86_64-linux-gnu`.
- Paquete Graphite2: `libgraphite2-3` `1.3.14-1+deb12u1` Debian Bookworm amd64, `.deb` SHA-256 `c19a7f6ba9298db7eef041ae27b08985f2c02009e418063f8bccdb5bc5e858dc` (acta de base nativa).
- TAR de imagen nativa **congelada** `i0-1b-native-base-freeze-01/i0-1b-native-base-graphite2-amd64.docker.tar`: **142.683.648 bytes**, SHA-256 `89cb892582b817cab4a0c9f566bf707415bb33eb06c5f3a799d8fefc92b74fe2`.
- Digest atribuido al índice de imagen / RepoDigest local: `sha256:5de4b1c725efc1ab7b9b1410aa5af48b3b5deb1ca6910b749d08168436633146`.
- Manifiesto de plataforma `linux/amd64`: `sha256:1b53025e95296aac372d8954b7dfcee4a9dfa3c20c2ea947dececf60c8391d87`.
- Configuración: `sha256:b9b8e831ac686867eb6e2f7892847f30e23e3063a930da9102baf0e30f2f4a92`; **6 capas**.
- Testigo `/usr/lib/os-release`: SHA-256 **`59a77b5f2666d9c85c489bd1911a6eebbd91ef22fe48b90a3b75f1b21f3844d4`**.

**No confundir:** SHA-256 del archivo TAR ≠ digest de índice OCI ≠ digest del manifiesto de plataforma ≠ `ImageID`/config ≠ DiffID ni blob comprimido. Una igualdad textual de RepoDigest local no acredita su registro remoto ni hace que BuildKit lo resuelva offline.

### 3.3 Reglas permanentes de operación

- Evidencia primaria, TAR, blobs, ZIP y binarios históricos: **fuera de Git; conservar sin mutación ni limpieza selectiva**. Las copias de análisis se alojan en directorios nuevos; los logs originales no se editan para corregirlos.
- Prohibidos sin nueva autorización: ejecutar Docker/Buildx/uv/pip/Tectonic, descargar paquetes, cambiar firewall o interfaces, mover/eliminar evidencias, hacer `prune`/`pull`/`push`, editar snapshot y repositorio, iniciar HV/E2E.
- El contexto Docker global `desktop-linux` y el builder Buildx `default` con driver `docker` son identidades distintas: no intercambiarlos ni cambiarlos implícitamente; observar sus valores por ejecución.
- Los **8 contenedores históricos detenidos** son inventario legítimo. Una política `0 contenedores registrados` es errónea; debe exigirse que estén detenidos y que el inventario sea estable.
- Aislamiento reportado en los gates Buildx: adaptadores Wi-Fi/Ethernet desconectados, rutas conocidas observadas, regla temporal outbound sobre `com.docker.backend.exe`, `--network none`; la regla debió recuperarse y verificarse en ambos almacenes. Esto **no** es telemetría exhaustiva de todas las posibles rutas de egress.

## 4. Cronología funcional anterior al laberinto BuildKit

| Orden lógico | Hito y evidencia | Resultado acreditable y observaciones |
|---|---|---|
| Preparación 16/10 | Snapshot I0-1; imagen Python amd64, `uv` y Tectonic archivados; evidencia Debian/Graphite2; plan de resolución inicial | Sujetos y recetas externas al proyecto. Algunos expedientes tienen solo planes, no pruebas de producto. |
| 17/10, G0/G1 | Adquisición TeX Live 2022: G1-01 recibió HTTP 412; G1 v02 obtuvo TAR completo | TAR físico `2.881.562.112` bytes, SHA-256 `425685e124746c15ba9bb8e0596bdaad98fce886afa347fbcf9ec0e9acd7fe79`; índice GZIP `1.276.215` bytes, SHA-256 `979a52178eb353c803dde1f66efe43ff7ae2ab908000323d4fef29e98e382ebd`. |
| 17/10, G2 | Lectura completa TAR/index y validación lógica; acta de `full-tar-acquisition-02` [E01] | `G2_INTEGRAL_CONTENT_CONSISTENCY_PASS`: 134.980 entradas TAR, 134.979 archivos de contenido, 1024 bytes de cierre cero; huella lógica `6ffe055852f8faf66c0acbe1a7fb27f87b869a90bad1204f3bf4d9683f597c7c`. Sin firma del publicador. |
| 17/10, G3 | Derivación del TAR a ZIP64 local [E02] | ZIP **2.793.653.488** bytes, SHA-256 `f3eb5dbfc57f87cd9968b9a4b03ed2a205ac3c30bcf68ea86b2adc853fb84b70`; equivalencia estática de contenido, todavía sin Tectonic en ese hito. |
| 17/10, base nativa | Tres tentativas de imagen; construcción exitosa 03; congelamiento [E03] | Base Python ampliada con Graphite2, 6 capas y TAR verificado. **No** se había construido el producto. |
| 17/10, loader | `ld-linux-x86-64.so.2 --list /audit/tectonic` sobre ELF Tectonic en base nativa [E04] | `TECTONIC_MINIMAL_DYNAMIC_LOADER_PASS`: siete rutas de librería resueltas y un intérprete; no equivale a compilar TeX ni a validar el programa. |
| 17/10, G4-R/X | Preflight estático y ejecución v02 de Tectonic para documento mínimo [E05] | `G4_X_OFFLINE_TECTONIC_MINIMAL_PDF_PASS`: PDF de 4.263 bytes, tras v01 detenida por check de commit anterior y corrección de contrato de atlas. Se observó un error Fontconfig **no fatal**. No E2E. |
| 17/10, G5-T | Prueba inicial `uv` versión/ayuda, sonda v01 [E06] | `G5_T_NOT_ACCEPTED_NO_RETRY`: código 2; `--constraint` singular no aparecía como texto literal en ayuda que anunciaba `--constraints` plural. La sonda se detuvo antes de `uv --version`. |
| 17/10, G5-T-R/C | Revisión de las tres ayudas capturadas y cierre documental [E07] | PASS parcial de reconciliación: error de aserción de texto, no error probado del binario ni de PyPI. Se conservó el STOP original. |
| 17/10, G5-A-X posterior | **Nueva** prueba controlada `uv` versión y ayuda en contenedor [E08] | `UV_VERSION_OBSERVED: uv 0.12.20 (x86_64-unknown-linux-gnu)`, salida `0`, opciones anunciadas y `G5_A_X_VERSION_AND_HELP_PASS_PROVISIONAL_IN_CONTAINER` en la consola y **`VERSION_AND_HELP_PASS_AFTER_WIFI_RESTORE_ONLY` en el JSON final incorporado por B**; no resolución real ni lock. Esta prueba **actualiza lo conocido** respecto de las actas más tempranas. |
| 17–19/10, G5-A/B diseños | A-R/A-D/A-I/A-V, B-R/B-C/B-D/B-E y metadatos Docker [E09–E12] | Decisiones y planes en varios estados: `REVIEW`, `PREPARED`, `PLANNING_ONLY` o evidencia de integridad limitada. No tratarlos automáticamente como aprobaciones ejecutables. |

**Precisión G4:** la hoja de ruta resumida del chat llama a algunas pruebas G4 «atlas/pipeline», pero las fuentes G4 aquí acreditan principalmente una **compilación mínima de Tectonic**; el PDF real se incorporó en B [E20]. No inferir ejecución integrada del pipeline Python a partir de ese resultado. Asimismo, una escritura `I0-1A COMPLETADO` anterior necesita examinar sus cierres I0-1A, distintos de las selecciones A/B.

## 5. G5-B — historia completa de errores y aprendizaje

### 5.1 Intentos de `FROM` literal y sus controles

Se buscaba ejecutar BuildKit con un Dockerfile cuyo `FROM` usara literalmente `i0-1b/native-base@sha256:5de4...` en ausencia operacional de enlace externo, exportar un testigo desde la imagen congelada y mantener estado Docker/repo. La siguiente tabla corresponde a los `FINAL_STATUS.txt` originales **copiados y comprobados por hash dentro de la recopilación A** [E13]:

| Expediente (prefijo) | ¿Se solicitó build? | Resultado primario; causa de STOP |
|---|---:|---|
| `G5_B_F_X_20261020T032015Z_...` | No | `PHYSICAL_LINK_NOT_DOWN` |
| `G5_B_F_X_20261020T034353Z_...` | No | `OCI_WITNESS_PREPARATION_FAILED` |
| `G5_B_F_X_V2_20261020T042615Z_...` | No | `DOCKER_SNAPSHOT_FAILED_before_buildkit_cache` (contextos/selección) |
| `G5_B_F_X_V3_20261020T045515Z_...` | No | `PREEXISTING_CONTAINERS_REQUIRES_REVIEW` (contrato equivocadamente rechazaba los detenidos) |
| `G5_B_F_X_V4_20261020T055214Z_...` | **Sí, exit 1** | `dockerfile contains no stages to build`; generación de Dockerfile con líneas incorrectas en PowerShell 5.1 |
| `G5_B_F_X_V5_20261020T185248Z_...` | No | `PHYSICAL_ADAPTER_IDENTITY_CHANGED` (ifIndex fijado indebidamente) |
| `G5_B_F_X_V5_20261020T185256Z_...` | No | Mismo STOP de identidad; no atribuir un build |
| `G5_B_F_X_V6_20261020T191700Z_...` | No | `ENGINE_INFO_FAILED_BEFORE_default`: Docker Desktop/motor no disponible en ese ensayo, no implica corrupción de OCI |
| `G5_B_F_X_V6_20261020T193356Z_...` | **Sí, exit 1** | BuildKit trató de consultar por `HEAD https://registry-1.docker.io/v2/i0-1b/native-base/manifests/...`, con fallo DNS al estar sin enlace |

**Correcciones instrumentales concretas:** generación del Dockerfile como bytes UTF-8 LF exactos (evitar precedencia de coma y `+` de PowerShell); usar GUID/identidad de adaptador y `ifIndex` observado dinámicamente, no números históricos; conservar contenedores detenidos; inspeccionar engine antes de cualquier gate; versionar cada paquete y nunca reutilizar permisos de ejecución.

**Resultado estructural:** el `FROM` literal (índice/RepoDigest) **no se consiguió offline** con este Buildx/BuildKit. `--pull=false` no impidió solicitud de metadatos de fuente; `--network none` delimita operaciones de build, no garantiza ausencia de consulta de resolución por el frontend. La línea `HEAD ...` en el log es **intento de solicitud**, no prueba de transmisión exitosa a Internet.

### 5.2 Decisión de arquitectura: contexto OCI local nombrado

Se preparó una copia en nuevo directorio, verificada por hashes de **14 archivos** de layout. Esta copia se conservó sin reescribir los blobs ni el TAR congelado. En vez del `FROM` literal, un Dockerfile instrumental aislado de **112 bytes** usa:

```dockerfile
FROM frozen_oci AS frozen_subject
FROM scratch
COPY --from=frozen_subject /usr/lib/os-release /probe/os-release
```

El build recibe `--build-context frozen_oci=oci-layout://.../layout@sha256:5de4...` y exporta únicamente la prueba del archivo al directorio externo mediante `--output type=local`. **Esto cambia el contrato técnico**: «BuildKit consume un OCI layout local nombrado»; NO «BuildKit resuelve el antiguo RepoDigest literal offline». Los ensayos son pruebas de infraestructura; no ejecutaron el producto.

### 5.3 Contexto OCI local v1 — error del parser Windows

Expediente [E14]: `G5_B_LOCAL_OCI_V1_20261020T204113Z_eff8b4d633714b718e4718f67c9b0f76`.

- Preflight nativo: integridad del paquete, Dockerfile, 20 casos sintéticos de red, 14 objetos OCI. Ejecutado **un solo build**; exit `1`. Política de estado y restauración de firewall verificadas.
- La referencia `oci-layout://C:/Users/.../layout@sha256:5de4...` contenía `C:`; Buildx `v0.29.1-desktop.1` separó equivocadamente la unidad en ruta/etiqueta OCI. El error original incluye `could not parse oci-layout reference "yt1...:/Users/...": invalid reference format`.
- **Conclusión:** fallo del parser/contrato de ruta Windows, anterior al consumo de capas. No era prueba de corrupción del TAR ni del índice; no se repitió el gate.

### 5.4 Contexto OCI local v2 — éxito funcional y STOP documental

Expediente [E15]: **`G5_B_LOCAL_OCI_V2_20261020T210654Z_33300c4b94074e2e9580954683d8864b`**.

- Cambio validado: contexto **relativo** `oci-layout://G5_B_OCI_LOCAL_WORKCOPY_01/layout@sha256:5de4...` y `WorkingDirectory` del proceso hijo fijado a la raíz externa. Comprobación de versión `buildx v0.29.1-desktop.1`, commit `28f6246ff24e2c05095e8741e48c48dcb2d3b4bc`.
- Motor: Docker Desktop Linux, builder Buildx `default` driver `docker`, BuildKit `v0.25.1` según contexto histórico. Contexto global observado `desktop-linux`; el controlador eligió `--context default` y **no** cambió el global.
- Controlador reportó una única solicitud de build, `PROCESS_single_build_EXIT_CODE: 0`, `OCI_WORKCOPY_AFTER: VERIFIED_14_FILES`, política de inventario exitosa (`CONTAINERS_STABLE: 8`, `IMAGES_STABLE: 10`, hash canónico del inventario igual antes y después) y `FIREWALL_RECOVERY: VERIFIED_RULE_ABSENT_BOTH_STORES`.
- El log BuildKit [E15] registra secuencialmente: `load metadata for docker.io/library/frozen_oci@sha256:5de4...`, **`[context frozen_oci] OCI load from client`**, `COPY --from=frozen_subject` y `exporting to client directory` (`copying files 335B`). No muestra una solicitud `HEAD https://registry-1...` como la de v6.
- **El gate original terminó en STOP:** `BUILD_LOG_CONTAINS_REMOTE_SOURCE_INDICATOR`. Su regex prohibía también el texto `load metadata for docker.io/`, que aquí se produjo como etiqueta de progreso del **contexto local**. Una cadena `docker.io/` no es prueba de conexión; tampoco su ausencia acredita ausencia de egress.
- **Revisión retrospectiva del operador, sin Docker:** verificó SHA-256 del log, esperado y exportado; comunicó `WITNESS_EQUALS_FROZEN_BYTES: True` y SHA-256 `59a77b5f2666d9c85c489bd1911a6eebbd91ef22fe48b90a3b75f1b21f3844d4`. **Ratificación independiente a nivel de las COPIAS en B:** `expected_os_release.bin` y `export/probe/os-release` miden **267 B cada uno**, son **idénticos byte a byte** y los dos SHA-256 calculados coinciden también con los renglones exactos del `SHA256SUMS.txt` primario incluido en B [E18].
- En A están `FINAL_STATUS.txt`, log del build, invocación, exit y comparación de estado. En B se añadieron **los bytes de ambos testigos y el manifiesto original del expediente**, por lo que el cotejo criptográfico ya no depende solamente de una transcripción. **Límite remanente:** B copia un único archivo bajo `export/`, pero no aporta listado autenticado de la totalidad del directorio exportado original; no afirmar formalmente que contenía *solo* ese archivo.

**Dictamen inmutable:** `G5_B_LOCAL_OCI_V2_STOP_OR_INCONCLUSIVE` (formal).  
**Adjudicación retrospectiva acotada:** `LOCAL_OCI_NAMED_CONTEXT_BUILD_EXIT_0_AND_WITNESS_MATCH_COPIES_VERIFIED`; testigos cotejados a partir de A/B y manifiesto del expediente. **No** modifica el STOP formal ni certifica egress cero. La condición de «export contiene exactamente un solo archivo» **no fue ejecutada formalmente** en v2 y continúa sin acreditarse respecto del directorio completo original.

## 6. uv y resolución Python: secuencia verdadera y decisión futura

### 6.1 Herramienta y ABI

- El archivo candidato `uv-x86_64-unknown-linux-gnu.tar.gz` tiene SHA-256 **`6590717592ace991ff83a63fef799e3ad9d33ecc8f96c5d6bdd732496e79337f`**, y el ELF interno SHA-256 **`b8299463da6fa7da3b94464444d252d0afca8ac6c96cb229f1baf4012f365246`** (según actas G5-R/T).
- El expediente de consola posterior **G5-A-X** registra **`UV_VERSION_OBSERVED: uv 0.12.20 (x86_64-unknown-linux-gnu)`**; Linux `x86_64`, CPython `3.11.17`, glibc `2.36` y SOABI `cpython-311-x86_64-linux-gnu`; las ayudas muestran `--constraints`, `--index-url`, `--python-version`, `--python-platform`, `--generate-hashes`, `--only-binary`, `--exclude-newer`, `--no-config`, `--no-python-downloads` y `--output-file`.
- **Reconciliación temporal obligatoria:** G5-T-C decía `UV_VERSION_NOT_CAPTURED` en el alcance del ensayo anterior. Esa frase no debe perpetuarse como estado final tras el G5-A-X posterior. Tampoco se puede escribir «resolver CLI aprobado»: se probó `--version` y lectura de ayudas, **no** la combinación semántica de flags ni el funcionamiento de `uv pip compile`.
- La consola A termina en `G5_A_X_VERSION_AND_HELP_PROVISIONAL_BEFORE_WIFI_RESTORE`. **B incorpora el registro original** `I0-1B_G5_A_X_RESULT_RECORD.json`: `result="VERSION_AND_HELP_PASS_AFTER_WIFI_RESTORE_ONLY"`, `docker_exit_code=0`, `wifi_restored=true`, `stop_reason=null`, `resolver_executed=false`, `flag_semantics_tested=false`, `lock_or_wheels_created=false`, `product_pipeline_tested=false` [E19]. De ese modo se resuelve el vacío temporal sin promocionar el ensayo anterior G5-T a PASS.

### 6.2 Decisiones de planificación (no de ejecución)

- Se seleccionó **índice único** `https://pypi.org/simple/`, sin índices secundarios, como decisión de *planificación* G5-A-I.
- Se eligió corte UTC fijo **`2026-10-17T00:00:00Z`**, aplicado a **fecha de subida del archivo** (no fecha de versión de paquete). Ausencia de metadatos confiables de carga: STOP o decisión aparte. El corte no reproduce una instantánea inmutable de PyPI ni asegura disponibilidad futura de ruedas.
- Se planificaron wheels binarios compatibles con la ABI objetivo, hashes SHA-256 y clausura transitiva; el formato de `requirements.lock` debe satisfacer el parser estricto `audit/build/verify_materials.py` **con evidencia real**, no por similitud de nombres.
- `groq==1.4.0` en `groq-constraint.in` no debe confundirse con un pin que el `pyproject.toml` original hubiera impuesto.
- Un único índice de consulta **no** asegura un único dominio de descarga. Revisar endpoints efectivos, redirecciones, TLS, proxy, caché, variables de entorno y registros antes de autorizar egress.

**Estado comprobado en A y B:** no se aporta `requirements.lock` validado, wheelhouse real, reporte de resolución ejecutada ni instalación. No comenzar I0-1C operativo sin contrato nuevo explícito.

## 7. Arquitectura: dos roadmaps que no deben mezclarse

**Roadmap de auditoría I0-1** (hoja de ruta proporcionada por el operador): I0-1A = adquisición/snapshot; I0-1B = base/infraestructura, TeX/Tectonic/OCI; I0-1C = resolución/obtención controlada de dependencias Python; I0-1D = instalación aislada y build de producto; I0-1E = validación funcional, seguridad, HV/E2E; I0-1F = SBOM, atestaciones y archivo final. Su cronología y criterio de cierre deben atender los **límites de esta evidencia**, no los íconos de color de un resumen previo.

**Roadmap arquitectónico del traductor** (`ROADMAP_ARQUITECTONICO_LP(1).md`, contexto de proyecto): Fase 16 core; Fase 17 extracción/corpus; Fase 18 runtime local; Fase 19 packaging/CLI/Docker; Fase 20 observabilidad; Fase 21 adaptación. I0-1 es una auditoría específica de materiales, infraestructura y ejecución de un checkpoint: **no significa que todas esas fases arquitectónicas estén terminadas**. Evitar inferir un CLI/sandbox de producción solo por haber observado `uv --help` o construido una base Docker.

**Principios rectores** (`PROJECT_SCOPE.md`, `ENGINEERING_PRINCIPLES.md`): separación puertos/adaptadores, núcleo puro y efectos en el perímetro, datos inmutables, determinismo, fail-closed, trazabilidad, no degradación silenciosa, FinOps/local-first. Un instrumento de auditoría que altera infraestructura del producto o no distingue evidencia de inferencia contraviene esos principios.

## 8. Lecciones operativas convertidas en reglas de ingeniería

| Error histórico | Regla preventiva antes de otro gate |
|---|---|
| Iniciar un gate sin Docker Desktop operativo | Preflight de disponibilidad del motor **antes** de cambiar firewall; fallar sin llamar build si está apagado. |
| Tratar 8 contenedores detenidos como contaminación | Capturar inventario antes/después y exigir estados y estabilidad; no exigir 0 objetos si la política solo demanda 0 ejecutándose. |
| `default` builder versus `desktop-linux` contexto global | Registrar `docker context show`, `--context`, builder, driver, versiones, imágenes y endpoints; no confundir metadatos de un contexto con prueba de capacidades del otro. |
| Generación defectuosa del Dockerfile por PowerShell | Validar bytes UTF-8, saltos LF, SHA-256, número real de etapas y sintaxis PS 5.1 **antes de ejecutar**. No asumir que pruebas Python en Linux validan PowerShell Windows. |
| `ifIndex` histórico cambiado después de reinicios | Comparar GUID/nombre/descr. y rutas en cada fase; `ifIndex` dinámico; STOP ante identidades ambiguas o enlaces nuevos. |
| Creer que `--pull=false` + `--network none` desactiva la búsqueda de metadatos | Separar red de instrucciones del Dockerfile, frontend, resolver de imagen, CLI, daemon y backend; exigir telemetría adecuada según afirmación de seguridad. |
| Sintaxis OCI con unidad Windows `C:` en Buildx v0.29.1 | Para ese parser, usar referencia relativa validada y fijar explícitamente el *working directory* de `Start-Process`; probar el contrato real del cliente antes de autorizar build. |
| Confundir `load metadata for docker.io/...` con conexión externa | Separar etiquetas de progreso, intentos de solicitud (`HEAD ...`), conexión efectiva y tráfico medido. No usar regex de texto como detector único de egress. |
| Considerar un STOP terminal como pérdida de todos los artefactos válidos | Mantener el STOP; hacer auditoría retrospectiva **solo lectura** del mismo expediente, con hashes originales, sin reejecutar el experimento. |
| Reusar un permiso de una versión fallida | Un permiso autoriza una ejecución y un controlador concreto; toda nueva ejecución exige decisión explícita. |
| Confundir `--constraint` con `--constraints` | Inspeccionar ayuda **y** código/versión real; validar la gramática de argumentos en el binario exacto. Una prueba sintética no equivale a uso del parser real. |
| Lectura de un acta antigua como “estado actual” | Correlacionar fechas y evidencia **posterior**: G5-A-X de `uv --version` supersede solo el estado informativo, no el STOP de G5-T. |
| Identidades `TAR` / `ImageID` / RepoDigest / OCI mezcladas | Declarar objeto y capa exactos de hashing: bytes TAR, índice, manifiesto amd64, config, capas, DiffID, file witness. |
| Demasiadas herramientas de revisión repetidas | Crear contrato de entrada, casos adversariales del bug real, alcance y criterio de aceptación; reutilizar evidencia original, no reconstruir/descargar cuando el dato ya existe. |
| Riesgo de perder contexto entre conversaciones | Exigir lectura de este documento y de los registros primarios relevantes **antes** de proponer plan/ejecución; registrar siempre qué evidencia nueva cambia el estado. |

**Prescripciones de reporte:** distinguir `NOT_EXECUTED`, `STOP_BEFORE_BUILD`, `BUILD_FAILED`, `BUILD_EXIT_0`, `WITNESS_MATCH`, `GATE_PASS` y `CERTIFIED`. Las etiquetas son **no equivalentes**. Informar siempre versión del instrumento, variante de contrato, número de intentos, resultado de restauración de firewall y límites de red.

## 9. Custodia, integridad y límites de esta edición

### 9.1 Fuentes y comprobaciones efectuadas en esta edición

- Subida `I0-1B_EVIDENCIA_DOCUMENTAL_A.zip`; **SHA-256 `9547a33ba11f00169d42b733705fc59ea5f72a9e6c125731de0ec47d5594d871`**.
- Paquete: **163 entradas**, de las que **160 son archivos de `payload/`** (994.434 bytes de contenido), `SHA256SUMS.staged.txt`, `collection_record.json` y un aviso de lectura. **Verificación efectuada aquí:** estructura ZIP válida, 160 digests del manifiesto interno coincidentes con los 160 bytes de copias, sin errores CRC; no se abrió Windows ni se certificó que el hash original anterior a la copia fuese independiente.
- `collection_record.json` declara fecha de creación `2026-10-21T16:18:18.265104+00:00`, `tier: A`, `files: 160`, `source_root` externo, `SOURCE_FILES_MODIFIED: 0` según salida del operador y advertencia explícita de que no atestigua procedencia original. La salida de PowerShell comunica `DOCUMENTARY_COLLECTION_PLAN_PASS_NO_FILES_WRITTEN`, después `DOCUMENTARY_COLLECTION_A_PREPARED_REVIEW_BEFORE_UPLOAD` y **cero comandos Docker**.
- **Paquete B focalizado:** `I0-1B_EVIDENCIA_DOCUMENTAL_B.zip`, SHA-256 **`f92b46fc7a4ab113aaa6cb59e4e727c1e46dca7f3e1d367454c7b884fc0e2e67`** calculado aquí. **29 entradas, 26 fuentes** (`payload/`, 58.670 B), manifiesto y registro de colección; **26/26 SHA-256 verificados**. `collection_record.json` declara `2026-10-21T16:44:26.512874+00:00`, `tier: B`. Se recomputaron directamente los hashes de testigos G5-B y PDF G4 y se cotejaron con los manifiestos primarios copiados; se leyeron los JSON de estado de `uv`, G4, imagen Docker y G5-T. No equivale a lectura independiente de todo el host.
- **Cierre histórico G5-B como fuente SECUNDARIA:** `I0-1B_G5_B_CIERRE_HISTORICO_2026-10-20.zip`, SHA-256 **`c37ef0a01561642690cc9ea7acca2cbc8e192697b6be4127a16ccdc02d0a1c00`**, **11 entradas y 10 objetos validados** contra `SHA256SUMS.release.txt`. Es un informe retrospectivo de asistencia, no un acta emitida automáticamente por Docker; se usa como guía de lecciones y se contrasta con E13–E15/E18 [E24].
- Los **1.211 nombres** del inventario exhaustivo sirven para mapa de custodia/selección, no prueba de bytes. Solo **160 copias A + 26 copias B** fueron recibidas en esta consolidación, correspondientes a **180 rutas distintas**; los seis archivos compartidos entre A y B tienen SHA-256 idéntico. El universo de 1.211 puede incluir varias versiones y fuentes no transferidas; el resto permanece externo en Windows.
- El operador **sí adjuntó después** el ZIP `I0-1B_G5_B_CIERRE_HISTORICO_2026-10-20.zip` en este turno. Su integridad interna fue verificada aquí. **No sabemos si lo archivó en la raíz externa Windows**: no aparece en el inventario anterior, que fue generado antes de esta entrega.

### 9.2 Jerarquía de fuentes y límites de autenticación

1. **Registros primarios en host** (TAR, ZIP, `.deb`, imágenes, logs, manifest, export) conservados sin modificación. Sus bytes no fueron todos incluidos en A/B; los hashes citados desde actas siguen siendo referencias, no una recomputación local completa de esos grandes originales.
2. **Copias seleccionadas A+B**: sus hashes se verificaron dentro de cada paquete; las actas son evidencias documentales derivadas; bitácoras `FINAL_STATUS`, logs y JSON son observaciones registradas por los instrumentos (sujetas a sus mecanismos de captura). En B, ciertos objetos se cotejaron **adicionalmente** contra manifiestos originales de su expediente.
3. **Consola retrospectiva del operador**: cotejo del testigo y recuperación de firewall; muy útil, sin firma independiente ni garantía externa de temporalidad.
4. **Diseños y tests sintéticos**: especifican lo que *debería* pasar, no lo que pasó en Docker Windows. Cada vez que `REVIEW_ONLY`, `PREPARED`, `PROPOSAL_NOT_APPROVED` o `SYNTHETIC` aparezca, no elevar a PASS operativo.

Los hash SHA-256 documentan identidad de bytes, **no** certifican por sí solos autenticidad upstream, que los datos hayan sido generados a la hora declarada ni ausencia de vulnerabilidades. Todo futuro traslado de evidencia requiere revisar secretos y rutas privadas; no publicar transcripciones de sistema indiscriminadamente.

## 10. Salvedades residuales y criterios de promoción a cierre integral

**Los vacíos P0 de bytes G5-B y resultado final de uv quedaron resueltos por B.** Los siguientes asuntos no impiden publicar una memoria técnica de continuidad v1.0, pero **sí limitan cualquier proclamación de cierre de auditoría integral**. No requieren repetir ensayos:

1. **P0 resuelto a nivel documental — G5-B v2:** B contiene las dos copias binarias, igualdad byte a byte y SHA-256 concordantes con `SHA256SUMS.txt` original [E18]. **No** se auditó directamente el directorio completo original de export, por lo que la exclusividad del archivo exportado sigue `NOT_VERIFIED`; una lectura autorizada y separada del host sería suficiente si se exige esa cláusula, sin nuevo build.
2. **P0 resuelto a nivel documental — G5-A-X:** B incluye el JSON final y manifiesto original: `VERSION_AND_HELP_PASS_AFTER_WIFI_RESTORE_ONLY`; solo versión/ayudas, con `wifi_restored=true` y sin resolver [E19]. `G5-T=NOT_ACCEPTED_NO_RETRY` se preserva [E23].
3. **P1 parcialmente resuelto — G1/G2/G3/G4:** B añade transcripciones y manifiestos que documentan G1/G2/G3, el ZIP64 TeX y el **PDF mínimo real**, SHA-256 `e75ed0...`, cotejado con su manifiesto [E20–E22]. No se volvieron a leer los TAR/ZIP de varios GiB del host ni se verificó firma upstream; no afirmar cadena de autenticidad externa.
4. **P1 parcialmente resuelto — imagen nativa / OCI:** B incorpora log `build-attempt-03`, `docker-image-inspect.json`, resultado `G5_B_D_M_LOCAL_METADATA_OBSERVATION_ONLY` y análisis local: se cotejaron nombres/digests y el carácter **no aprobatorio** de esa observación [E25]. La integridad completa de blobs OCI/TAR de 142 MB sigue fundada en los verificadores y expedientes ejecutados del operador, no en una nueva lectura del TAR aquí.
5. **P1 abierto — I0-1A:** el checkpoint/cierre específico de I0-1A no fue incluido en A/B. No homologar «I0-1A COMPLETADO» a certificado independiente de todo el producto hasta consultar ese archivo y su contrato.
6. **P2 abierto — límites de seguridad:** desconexión física de enlaces, controles de rutas y firewall respaldan el ensayo acotado, **no** una captura exhaustiva de egress de todos los procesos. `network=none` tampoco prueba ausencia de resolución de metadatos por el frontend.
7. **P2 — Sin recopia masiva:** si una decisión futura exige un dato aún no cubierto, pedir solo el archivo primario y manifiesto pertinentes; evitar importar el historial completo o reproducir builds solo por motivos documentales.

**Criterio para dar la edición v1.0 por aceptada por el proyecto:** revisión humana del operador, cotejo de las limitaciones anteriores y conservación del SHA-256 de publicación. «v1.0 documental» **no equivale** a `I0-1A..F CERTIFIED`. Una incorporación posterior al repositorio requiere **autorización separada** y debe incluir solo este Markdown, nunca las pruebas primarias.

## 11. Protocolo de continuidad (obligatorio para I0-1C, CLI y sandbox)

Antes de actuar, el próximo ingeniero o asistente debe:

1. Leer §§1–3, 5.4, 6, 8, 10 y las fuentes [E08], [E15] y [E09–E12] pertinentes; comprobar si existe versión posterior del canónico. **No basarse solo en resúmenes de chat.**
2. Reafirmar el contrato: **OCI context nombrado** demostró testigo; `FROM` literal por RepoDigest sigue **sin acreditar offline**. No diseñar un Dockerfile futuro que asuma que ambos mecanismos son equivalentes.
3. Antes de I0-1C: determinar entrada exacta del snapshot, versión de uv, ABI/arquitectura, sintaxis real, índice y corte, redirecciones/dominios, política de caché/proxy, formato de lock compatible con `audit/build/verify_materials.py`, hashes y rutas de wheelhouse. Registrar cuáles son decisiones adoptadas *para diseño* y cuáles requieren aprobación.
4. Preparar un documento de diseño de I0-1C independiente con preflight sin red y una futura autorización **delimitada**, no lanzar resolución/adquisición por estar G5-B funcionalmente cerrado.
5. Dejar fuera de alcance en I0-1C: instalación de wheels, build del producto, CLI real del traductor, sandbox, runtime `network=none`, HV/E2E, certificación/SBOM. Cada uno tendrá su propio contrato y prueba.
6. Al finalizar un hito, añadir al canónico **hecho + fuente + hash + clasificación + resultado + límites + nuevo estado**, sin borrar las entradas de fallos. Mantener los datos voluminosos en custodia externa.

**Condición de parada general:** ausencia de fuente primaria requerida, digest inesperado, miembro de evidencia alterado, veredicto ambiguo, versión de herramienta no concordante o autorización no otorgada implica **STOP sin prueba sustitutiva automática**.

## 12. Índice de evidencias — referencias de primer acceso

`ROOT = C:\Users\Admin\Desktop\Proyectos` (ruta histórica; puede ser distinta en otra estación). Los archivos listados con `[A]` o `[B]` fueron copiados a su ZIP respectivo, con los hashes bajo `SHA256SUMS.staged.txt`. Las fuentes `[H]` corresponden al cierre retrospectivo secundario. Para verificar un archivo del host, hacerlo contra el manifiesto de **su propio expediente**, no contra un hash supuestamente universal.

| ID | Ruta relativa desde ROOT | Qué acredita / límite |
|---|---|---|
| **E01** | `full-tar-acquisition-02/I0-1B_ACTA_CIERRE_G2_INTEGRIDAD_TAR_TEX_2026-10-17.md` | [A] Cierre G2; ejecución comunicada y alcance de hash físico/lógico, sin captura original firmada. |
| **E02** | `i0-1b-tectonic-resources/tlextras-2022.0r0/zip-derivation-01/I0-1B_ACTA_CIERRE_G3_ZIP_LOCAL_TEX_2026-10-17.md` | [A] G3 ZIP local derivado, equivalencia estática. |
| **E03** | `i0-1b-native-base-freeze-01/I0-1B_ACTA_CIERRE_BASE_NATIVA_2026-10-17.md`; `freeze-session.txt` | [A] Tres tentativas, base Graphite2 congelada, claves OCI/identidad y límites. TAR grande no copiado. |
| **E04** | `i0-1b-tectonic-loader-check-01/I0-1B_ACTA_CIERRE_VALIDACION_DINAMICA_TECTONIC_2026-10-17.md` | [A] Prueba mínima de enlazador; no runtime completo. |
| **E05** | `i0-1b-tectonic-g4-functional-01/I0-1B_ACTA_CIERRE_G4_X_TECTONIC_OFFLINE_PDF_MINIMO_2026-10-17.md`; `docker-tectonic-console.txt` | [A] PDF mínimo y logs; no PDF completo dentro de A. |
| **E06** | `i0-1b-uv-g5-t-cli-01/powershell-session.txt`; `docker-uv-cli-console.txt` | [A] `G5_T_NOT_ACCEPTED_NO_RETRY`, error singular/plural. |
| **E07** | `i0-1b-tectonic-functional-review/I0-1B_G5_T_C_ACTA_CIERRE_DOCUMENTAL_LIMITADO_2026-10-17.md` | [A] Diagnóstico del STOP original; afirmaciones limitadas temporalmente. |
| **E08** | `i0-1b-uv-g5-a-x-cli-01/powershell-session.txt`; `docker-uv-version-help-console.txt` | [A] **Evidencia posterior** de `uv 0.12.20`, versión/ayudas y PASS provisional previo a restaurar Wi-Fi; cierre final complementado por E19, sin resolver. |
| **E09** | `i0-1b-tectonic-functional-review/I0-1B_G5_A_D_DECISIONES_RESOLUCION_Y_WHEELS_REVIEW_2026-10-17.md` | [A] Diseño G5-A-D aún propuesto; no adoptar como permiso. |
| **E10** | `i0-1b-tectonic-functional-review/I0-1B_G5_A_I_DECISION_INDICE_Y_CORTE_UTC_2026-10-17.md` y `.json` | [A] PyPI único/corte fijado para planificación. |
| **E11** | `i0-1b-tectonic-functional-review/I0-1B_G5_A_V_INFORME_CONTRATO_ESTATICO_REVIEW_2026-10-17.md`; `I0-1B_G5_A_X_DISENO_VALIDACION_CLI_OFFLINE_REVIEW_2026-10-17.md` | [A] Alcance de contrato y pruebas preparadas, no sustituyen runtime observado E08. |
| **E12** | `i0-1b-tectonic-functional-review/I0-1B_G5_B_E_R_PLAN_VINCULO_OCI_REPODIGEST_TAR_REVIEW_2026-10-19.md`; `i0-1b-docker-g5-b-d-metadata-01/I0-1B_G5_B_D_M_EVIDENCE_SHA256SUMS.txt` | [A] Pregunta de vínculo OCI/RepoDigest y localización de inspección original; parte de diseño. |
| **E13** | `i0-1b-tectonic-functional-review/G5_B_F_X_*/FINAL_STATUS.txt`; `G5_B_F_X_V[2-6]_*/FINAL_STATUS.txt`; `G5_B_F_X_V4_*/single_build.stderr.txt`; `G5_B_F_X_V6_20261020T193356Z_*/single_build.stderr.txt` | [A] Evolución de STOP y fallos reales de Dockerfile y HEAD remoto. Los prefijos `*` son guía de localización, no una función de glob para automatizar escrituras. |
| **E14** | `i0-1b-tectonic-functional-review/G5_B_LOCAL_OCI_V1_20261020T204113Z_eff8b4d633714b718e4718f67c9b0f76/{FINAL_STATUS.txt,single_build.stderr.txt,build_invocation.txt,SHA256SUMS.txt}` | [A] v1 OCI Windows con `C:` rechazado. |
| **E15** | `i0-1b-tectonic-functional-review/G5_B_LOCAL_OCI_V2_20261020T210654Z_33300c4b94074e2e9580954683d8864b/{FINAL_STATUS.txt,single_build.stderr.txt,build_exit_code.txt,build_invocation.txt,SHA256SUMS.txt,state_policy_compare.stdout.txt,oci_workcopy_verify_after.stdout.txt}` | [A] v2 éxito del build, copia desde cliente y STOP por indicador textual; referencia original al export/esperado en manifiesto. |
| **E16** | `i0-1-source/metadata/source_manifest.json`; `i0-1-source/src/pyproject.toml`; `i0-1b-resolution-plan/requirements.in`; `groq-constraint.in` | [A] Fuente congelada, recuento 328 y 24 dependencias; `requirements.in` no es lock. |
| **E17** | `i0-1b-tectonic-functional-review/G5_B_OCI_LOCAL_PREPARATION_v1/README_ES.md`; `G5_B_LOCAL_OCI_GATE_V1/README_ES.md`; `G5_B_LOCAL_OCI_GATE_V2/README_ES.md` | [A] Contratos de instrumento, preparación y alcance de controles; no sustituye resultados E14/E15. |
| **E18** | `i0-1b-tectonic-functional-review/G5_B_LOCAL_OCI_V2_20261020T210654Z_33300c4b94074e2e9580954683d8864b/{expected_os_release.bin,export/probe/os-release,SHA256SUMS.txt}` | [B] **Doble testigo real**: 267 B cada uno, igualdad directa y SHA-256 igual en ambas copias y manifiesto original. No implica unicidad del directorio export. |
| **E19** | `i0-1b-uv-g5-a-x-cli-01/{I0-1B_G5_A_X_RESULT_RECORD.json,I0-1B_G5_A_X_EVIDENCE_SHA256SUMS.txt,probe-outputs/uv-version.txt,probe-outputs/uv-compile-help.txt}` | [B] Cierre final VERSION_AND_HELP_PASS_AFTER_WIFI_RESTORE_ONLY, uv 0.12.20; sin resolver ni adquirir. |
| **E20** | `i0-1b-tectonic-g4-functional-01/{I0-1B_G4_X_RESULT_RECORD.json,I0-1B_G4_X_EVIDENCE_SHA256SUMS.txt,output/I0-1B_G4_MINIMAL_OFFLINE.pdf,output/I0-1B_G4_MINIMAL_OFFLINE.log,I0-1B_G4_X_V02_TRANSCRIPCION_SALIDA_APORTADA_2026-10-17.txt}` | [B] PDF mínimo de 4.263 B y hash del expediente; JSON provisional y transcripción final con Wi-Fi restaurado; no E2E. |
| **E21** | `i0-1b-tectonic-resources/tlextras-2022.0r0/full-tar-acquisition-02/{session.txt,SHA256SUMS.txt}`; `full-tar-acquisition-02/I0-1B_G2_TRANSCRIPCION_SALIDA_APORTADA_2026-10-17.txt` | [B] G1 transporte de TAR grande, G2 verificación integral reportada; la transcripción G2 no es captura automática. |
| **E22** | `i0-1b-tectonic-resources/tlextras-2022.0r0/zip-derivation-01/{I0-1B_G3_TRANSCRIPCION_SALIDA_APORTADA_2026-10-17.txt,I0-1B_G3_ZIP_DERIVATION_MANIFEST.json,I0-1B_G3_CIERRE_DOCUMENTAL_SHA256SUMS.txt}` | [B] G3 ZIP64 y equivalencia reportada; no se incorporó el ZIP de 2,79 GB. |
| **E23** | `i0-1b-uv-g5-t-cli-01/I0-1B_G5_T_RESULT_RECORD.json` | [B] STOP formal antiguo `NOT_ACCEPTED_NO_RETRY`, Docker exit 2, Wi-Fi restaurado, sin resolver. |
| **E24** | ZIP secundario `I0-1B_G5_B_CIERRE_HISTORICO_2026-10-20.zip`, acta/ADR/runbook internos | [H] Síntesis histórica y lecciones, 10 objetos hash verificados; **no** expediente de ejecución ni firma del host. |
| **E25** | `i0-1b-native-build-attempt-03/{build.log,session.txt}`; `i0-1b-docker-g5-b-d-metadata-01/{I0-1B_G5_B_D_M_RESULT_RECORD.json,docker-image-inspect.json,local-metadata-analysis.json}` | [B] Build 03 y metadata Docker local; resultado D-M `OBSERVATION_ONLY_NOT_BASE_IMAGE_APPROVAL`. |

### Anclas de integridad de especial interés

| Objeto | SHA-256 | Tipo / procedencia |
|---|---|---|
| ZIP documental A | `9547a33ba11f00169d42b733705fc59ea5f72a9e6c125731de0ec47d5594d871` | Recomputado al recibir el ZIP; 160 fuentes. |
| ZIP documental B | `f92b46fc7a4ab113aaa6cb59e4e727c1e46dca7f3e1d367454c7b884fc0e2e67` | Recomputado; 26 fuentes, 29 entradas ZIP. |
| ZIP cierre G5-B secundario | `c37ef0a01561642690cc9ea7acca2cbc8e192697b6be4127a16ccdc02d0a1c00` | Recomputado; 10 objetos bajo manifiesto interno. |
| Snapshot manifest `i0-1-source/metadata/source_manifest.json` | `b92e1a2c3c2998b6d54839b62cd70bfb7cf7d45e1b33b50831f22e44ff459139` | Archivo incluido en A, cotejado contra `SHA256SUMS.staged.txt`. |
| TAR TeX físico G1/G2 | `425685e124746c15ba9bb8e0596bdaad98fce886afa347fbcf9ec0e9acd7fe79` | Informado en G2; TAR no copiado. |
| Huella lógica bundle TeX | `6ffe055852f8faf66c0acbe1a7fb27f87b869a90bad1204f3bf4d9683f597c7c` | Informada en G2; no equivale a hash TAR/ZIP. |
| ZIP64 TeX local G3 | `f3eb5dbfc57f87cd9968b9a4b03ed2a205ac3c30bcf68ea86b2adc853fb84b70` | Informado en G3; ZIP no copiado. |
| TAR Docker nativo congelado | `89cb892582b817cab4a0c9f566bf707415bb33eb06c5f3a799d8fefc92b74fe2` | Informado y reutilizado; TAR no copiado. |
| OCI índice de imagen | `5de4b1c725efc1ab7b9b1410aa5af48b3b5deb1ca6910b749d08168436633146` | Objeto OCI, no hash del TAR. |
| Testigo esperado/exportado | `59a77b5f2666d9c85c489bd1911a6eebbd91ef22fe48b90a3b75f1b21f3844d4` | **Verificación directa de ambas copias B**, 267 B iguales, y chequeo contra el manifiesto original [E18]. |
| PDF mínimo Tectonic G4-X | `e75ed08051ff22e9817dc745b8e6b6559a82271a95d12cf7a6b343e7edb53d02` | PDF de 4.263 B incluido en B y cotejado con manifiesto G4-X [E20]; no es análisis forense exhaustivo del PDF. |
| Dockerfile instrumental OCI local | `f29a1416f190bc741579a1151843466805d35bcf54202613d8edb9f4f6ebe394` | Contenido validado, 112 bytes, 3 instrucciones. |

---

## 13. Instrucción de mantenimiento del canónico

Cada actualización debe añadir una entrada legible con **fecha UTC, hito, cambio de conocimiento, estado anterior, estado nuevo, fuente primaria, hash o ruta de manifiesto, permisos consumidos, invariantes revisadas y asuntos abiertos**. Si un hecho posterior contradice un acta anterior, anotar «la afirmación era correcta *hasta* la fecha de esa acta» o «fue refutada», **sin borrar la evidencia de cómo se llegó a ella**.

**Antes de hacer commit:** revisar personalmente si corresponde añadir el Markdown al árbol documental existente; no trasladar TAR, Docker archives, wheels, PDF, logs privados, ejecutables ni secretos al historial de Git. El documento es portátil; los binarios no lo son. Hacer un cambio documental aislado solo bajo autorización.

**Próxima acción recomendada:** revisión/aceptación humana de este v1.0 y su hash de publicación; **después** diseñar I0-1C con autorización propia, leyendo G5-A-D/I y las salvedades de §10. No repetir Docker/Tectonic/uv por conveniencia documental.
