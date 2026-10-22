# I0-1C — Acta técnica de cierre de dependencias Python

**Fecha de cotejo documental:** 2026-10-22  
**Estado:** `CIERRE TÉCNICO I0-1C ACEPTADO POR EL OPERADOR — PUBLICACIÓN GIT PENDIENTE`  
**Resultado aceptado:** `I0-1C_DEPENDENCIAS_PYTHON_ADQUIRIDAS_Y_VERIFICADAS_EN_ALCANCE_C1`  
**Nivel de acreditación:** solo resolución, adquisición y verificaciones estáticas descritas; **NO_ACREDITADA_PRODUCCIÓN**.  
**Repositorio y rama local informada:** `RDsanchez-git/translator_pdf`, `pipeline_stabilization`.  
**Estado Git comunicado:** `audit/build/verify_materials.py` modificado localmente; sin commit, push o merge para I0-1C. Este expediente no ejecutó ninguna operación Git.

## 1. Frontera de alcance

I0-1C tiene por finalidad fijar, resolver, seleccionar, adquirir e inspeccionar **las dependencias Python** del sujeto congelado de I0-1. **No** acredita instalación, dependencias ELF en ejecución, procedencia autenticada, runtime final de imagen, Tectonic dentro del contexto final, build Docker, traducción PDF→PDF, HV, E2E, ni SBOM. Esos controles deberán mantenerse en sus etapas sucesivas, en particular I0-1D, I0-1E e I0-1F conforme a la planificación ya documentada.

**Sujeto I0-1 declarado:** commit `c56f3e124d76ae9f1506e4b12fbf0faa4881b574`, árbol `eb7d2f6770517b72546055f4b611bac4734a3db3`, 328 archivos de origen y 24 requerimientos directos. `groq==1.4.0` es **restricción instrumental** de esta resolución, no pin histórico acreditado.

**Destino fijado de resolución/selección:** CPython `3.11.17`, `x86_64-manylinux_2_36`; PyPI `https://pypi.org/simple/`; corte `2026-10-17T00:00:00Z`; ejecutable `uv 0.12.20` (ELF SHA-256 `b8299463da6fa7da3b94464444d252d0afca8ac6c96cb229f1baf4012f365246`). La inspección realizada desde Windows empleó **tags de destino simulados**, no una ejecución de gate productivo en Linux/amd64 CPython 3.11.17/glibc 2.36.

## 2. Evidencia recibida y hashes recalculados

Se recalcularon directamente los SHA-256 de los **cinco archivos adjuntados a esta conversación** y se analizaron los documentos de resolución, selección y adquisición.

| Archivo | Bytes | SHA-256 recalculado |
|---|---:|---|
| `requirements.lock` | 209.095 | `a91a5e4f160029108f122724fa12717f37082b544274ccf8b09125191cf02fae` |
| `C1_R_RESULT.json` | 1.698 | `3023e106ef8aa5eebfa0fdd6485366dcb81f35591ff0a0ed1b75b828f8032635` |
| `C1_D_M_RESULT.json` | 33.397 | `2967ee1304fd9f5280af02da17862ed6b34b0e389e0c668e90d2d656192002f4` |
| `C1_D_M_SELECTION.json` | 87.572 | `f5c80a6acf1668526470e81c65cd35639799a4bb904dc67bb316244f2644cdaf` |
| `C1_D_W_RESULT.json` | 3.618 | `4608a14e64d722627ad4968feb7b12b39162f43f51eb3205c9d4e4d9a9c4446f` |

**Cadena de referencia verificada, sin saltos:**

- `C1_D_M_RESULT.source_c1r_json_sha256` coincide con el hash real de `C1_R_RESULT.json`.
- `C1_D_M_RESULT.source_lock_sha256`, `C1_D_M_SELECTION.source_lock_sha256` y `C1_D_W_RESULT.source_lock_sha256` coinciden con el lock real.
- `C1_D_M_SELECTION.source_metadata_result_sha256` coincide con el hash real de `C1_D_M_RESULT.json`.
- `C1_D_W_RESULT.source_selection_sha256` coincide con el hash real de `C1_D_M_SELECTION.json`.
- La identidad del manifiesto de origen se conserva con SHA-256 `b92e1a2c3c2998b6d54839b62cd70bfb7cf7d45e1b33b50831f22e44ff459139` en la cadena documental.

## 3. Reconciliación de contenido, resultados y corte

| Control | Resultado observado |
|---|---|
| Resolución C1-R/02 | `exit_code=0`; 158 pins en el lock; `groq==1.4.0` |
| Colección C1-D/M/02 | 158 solicitudes completadas; 4.203.428 bytes de respuestas JSON declarados y suma coincidente de inventario |
| Selección C1-D/M/02 | 158 entradas, sin distribución ni nombre de wheel repetidos |
| Equivalencia de nombres y versiones | 158/158 coinciden entre catálogo, selección y pins del lock; versiones contrastadas con PEP 440 |
| SHA-256 de wheels seleccionados | 158/158 aparecen en los hashes admitidos por su pin del lock |
| Fecha de publicación | Ninguna `upload_time_iso_8601` de la selección supera `2026-10-17T00:00:00Z` |
| Rutas de distribución | 158/158 URLs HTTPS bajo `files.pythonhosted.org`, basename de URL igual al wheel declarado |
| Tags declarados | `best_tag` incluido en los tags del nombre del wheel seleccionado en los 158 registros |
| Tamaño total calculado | 3.367.898.588 bytes; coincide entre selección y resultado de adquisición |
| Archivo individual máximo | 554.581.699 bytes; coincide con el máximo declarado por selección |
| C1-D/W/01 | 158 nombres de paquetes distintos; conjunto idéntico al seleccionado; `downloaded_wheels=158` |
| Alcance de ejecución declarado | Instalaciones 0, Docker no ejecutado; aislamiento independiente de red no acreditado |

**Advertencia de evidencia:** la integridad de los **bytes de los 158 `.whl` locales**, sus `RECORD` y el cierre transitivo está sustentada por las salidas operativas del usuario —`C1_D_W_OFFLINE_HASH_INVENTORY_PASS_ONLY` y `C1_D_S_REPOSITORY_PATCHED_CROSS_TARGET_PASS_ONLY`—, **no** por una lectura directa de esos 3,14 GiB desde este entorno. Los 158 JSON individuales de respuesta PyPI tampoco se adjuntaron; sus hashes y longitudes sí están inventariados en `C1_D_M_RESULT.json`. Ninguna limitación se transforma en PASS por el cotejo documental.

## 4. Inspección C1-D/S y política local del verificador

La salida de la inspección sobre el verificador **localmente modificado** informó 158/158 wheels, 3.367.898.588 bytes, metadatos y hashes internos `RECORD` PASS, tags del destino **simulado** PASS y cierre transitivo de 158 PASS. `inspect_wheel()` se importó directamente de `audit/build/verify_materials.py`, **sin shadow patch**. El archivo modificado continúa **sin commit**.

**Base del archivo antes de cambio:** Git blob `cc4ca4e108b9f8813ced0ae0a1d5f9e84478896f`.  
**Parche revisado:** SHA-256 `7ffa360390c346ca6bb4389908c052e8650ba3ef8153d6c7b2ced79bf109c190`.  
**Diff informado:** 29 inserciones, 6 eliminaciones, un único archivo.

Tratamiento del verificador, justificado mediante evidencia:

1. `jsonref`: reconocer `Root-Is-Purelib: True` por interpretación booleana insensible a mayúsculas.
2. `setuptools`: localizar los tres metadatos del `.dist-info` principal, sin confundir los 12 encabezados `WHEEL` de paquetes vendorizados.
3. `scipy`: ratio máximo 240:1 solo en los tres miembros NIST ANOVA identificados y solo con el SHA-256 del wheel autorizado.
4. `torch`: máximo 13.100 miembros solo para su wheel identificado por nombre completo y SHA-256 (13.043 miembros observados, rutas duplicadas 0).

**Pruebas informadas:** 3 positivas, 10 negativas y 4 wheels reales focales PASS; luego 158 wheels PASS con el archivo local integrado. No se ejecutaron nuevas pruebas sobre el wheelhouse en el proceso de generación de esta acta.

## 5. STOP históricos preservados

Permanecen en el expediente original sin reclasificar: C1-R/01 (opciones de `uv` incompatibles); C1-D/M/01 (`cuda-toolkit`, comparación textual de versión); C1-D/S anterior (`jsonref`, `setuptools`, `scipy`, `torch` bajo política original); y el error de transcripción de un SHA-256 en una instrucción PowerShell. Los PASS posteriores no eliminan los STOP históricos ni acreditan su causa como inexistente.

## 6. Limitaciones y responsabilidades de etapas posteriores

- `INDEPENDENT_EGRESS_ISOLATION_PROVEN=NO`: no se demostró aislamiento de red independiente durante las operaciones conectadas.
- Procedencia de PyPI y autenticidad del publicador **no acreditadas** solo con API, TLS, fechas y hashes; el corte temporal no equivale a un repositorio inmutable.
- Identidad efectiva de runtime Linux/amd64, glibc 2.36, CPython 3.11.17 y digest de imagen: **no verificada en host productivo**.
- Materiales v1.1 `APPROVED_MATERIALS`, binario `tectonic` integrado, instalación, ELF, build, HV, E2E PDF→PDF y SBOM: **no ejecutados/no emitidos aquí**, reservados a sus controles correspondientes.
- Cambios de repositorio: commit, push y merge **no ejecutados** para I0-1C; requieren cierre documental aceptado y revisión de diff contra `main` para evitar commits no relacionados.
- Custodia: wheelhouse de 3,14 GiB y expedientes originales bajo `I0-1_ARCHIVO_AUDITORIA` en equipo del operador, no redistribuidos en Git.

## 7. Dictamen técnico aceptado y publicación pendiente

**Dictamen de revisión aceptado:** `COTEJO_PRIMARIO_C1_R_D_M_D_W_PASS_SIN_DISCREPANCIAS`, limitado a los cinco archivos disponibles y a los resultados de consola comunicados. Se considera satisfecho **técnicamente el alcance de reproducibilidad estática de dependencias Python** de I0-1C, con las limitaciones del §6. **No constituye acreditación de producción ni PF-06.**

**Aceptación del alcance técnico:** el operador aceptó expresamente el cierre técnico de I0-1C en esta conversación el 2026-10-22, condicionado a que no hubiera otros requisitos dentro del alcance estático descrito. La aceptación **no** acredita la imagen Linux real, instalación, build, procedencia autenticada, aislamiento de red, HV/E2E ni SBOM. Los expedientes originales y el wheelhouse permanecen bajo custodia local del operador; no se verificó de nuevo su persistencia ni su protección contra alteraciones al emitir esta acta. La publicación controlada de esta acta y del cambio instrumental en Git permanece pendiente y es una operación separada del dictamen técnico.

**Registro de aceptación humana:** `ACEPTACIÓN EXPRESA EN CONVERSACIÓN, 2026-10-22; SIN FIRMA DIGITAL NI AUTÓGRAFA`.  
**Commit/push/merge:** `NO_EJECUTADOS PARA I0-1C; PUBLICACIÓN PENDIENTE`.

## 8. Continuidad aprobada como propuesta, no ejecutada

La siguiente acción es preparar una integración Git **limitada a este acta y al cambio de `audit/build/verify_materials.py`**. Antes del commit/PR se deberán revisar el árbol local, el estado del índice y la diferencia efectiva respecto de `main`; no incluir lock, wheelhouse, respuestas PyPI ni expedientes de adquisición en el repositorio. La etapa posterior es **I0-1D**, instalación aislada y build del producto con los materiales aprobados, sujeto a su propio contrato y autorización. No se ejecutó ni se autorizó I0-1D mediante la aceptación de I0-1C.
