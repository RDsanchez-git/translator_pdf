# HITO_0.4.5_P6_ASSEMBLY_COMPILER_AUDIT.md
## Assembly, Serialization, TeX Rendering & Compiler Artifact Boundary — Reporte de Auditoría Forense Integral Bloque P6

* **Estado:** AUDIT CLOSED / REMEDIATION BACKLOG OPEN (Bloque P6)
* **Fecha de Emisión:** 2026-07-29
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.4.5 (Production Pipeline Audit — Bloque P6)
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Auditoría analítica y forense estricta sustentada en el examen directo del código fuente de producción (`apps/compiler/__main__.py`, `apps/compiler/docker_runner.py`, `apps/compiler/log_parser.py`, `apps/compiler/tex_builder.py`, `core/compiler/assembler.py`, `core/compiler/rendering/implementations.py`, `core/compiler/rendering/mapper.py`, `core/compiler/service.py` e `infra/serialization/ast_json.py`), aplicando el protocolo de investigación de 15 capas. Cero suposiciones. Cero mutaciones en código productivo.

---

## 1. MARCO EPISTEMOLÓGICO Y DIAGNÓSTICO DE RUNTIME

Sometiendo el Bloque P6 al protocolo de investigación de 15 capas (Capa 1: Separación de Evidencia e Interpretación; Capa 7: Detección de Contaminación; Capa 11: Falsación Sistemática; Capa 14: Invariantes), el examen directo del código fuente de producción **ha confirmado una desconexión crítica entre la capa de aplicación/dominio (`CompilationService` / `DocumentAssembler`) y el plano de ejecución física (`AssemblerWorkerDaemon`)**.

La arquitectura declarada preveía que el ensamblado se gestionara centralizadamente con validación de secuencia, verificación de hashes criptográficos y políticas de tolerancia (`AssemblyPolicy`). Sin embargo, el daemon de compilación en producción (`apps/compiler/__main__.py`) **bypassea por completo el núcleo del compilador** (`CompilationService` y `DocumentAssembler`), realizando una reconstrucción ad-hoc de fragmentos, invocando directamente a `TexBuilder` y ejecutando `Tectonic` localmente con riesgos severos de condiciones de carrera en el sistema de archivos.

```text
==================================================================================================
                 FLUJO TEÓRICO DECLARADO PARA EL BLOQUE P6 (FALSADO)
==================================================================================================

  [Materialized/Projection DB] ──► [CompilationService] ──► [DocumentAssembler]
                                           │                   (AssemblyPolicy)
                                           ▼
                                 [RenderUnitMapper]
                                           │
                                           ▼
                                 [RenderContext / TexBuilder] ──► [DockerRunner] ──► PDF

==================================================================================================
                 FLUJO REAL OBSERVADO EN RUNTIME (DEMOSTRADO POR CÓDIGO)
==================================================================================================

  [MaterializedPlaneRepository] + [ASTRegistry]
         │
         ▼
  [AssemblerWorkerDaemon._process_assembly_task()] (apps/compiler/__main__.py)
         │
         ├──► [BYPASS ✗] ──► CompilationService (core/compiler/service.py) [ZOMBI EN DAEMON]
         ├──► [BYPASS ✗] ──► DocumentAssembler / AssemblyPolicy [ZOMBI EN DAEMON]
         │
         ├──► Construcción ad-hoc manual: valid_chunks.append(RenderUnit(...))
         │
         ▼
  [TexBuilder.build(valid_chunks)]
         │
         ▼
  [DockerRunner.compile(tex_content)] (apps/compiler/docker_runner.py)
         │
         ├──► [RIESGO P0 ✗] Invocación nativa 'tectonic' sin aislamento Docker
         ├──► [RIESGO P0 ✗] Escritura de 'tectonic_crash.log' y PDF final en os.getcwd()
         │                  (Condición de carrera entre workers paralelos)
         │
         ▼
  [FSM Machine Transition] ──► CompleteDocumentCommand / FailDocumentCommand
```

---

## 2. REGISTRO EXHAUSTIVO DE HALLAZGOS FORENSES (P6-H01 A P6-H06)

### P6-H01: Desconexión y Orfandad del Core de Compilación (`CompilationService` y `DocumentAssembler` Bypasseados) [DEMOSTRADO]
* **Ubicación:** `apps/compiler/__main__.py` vs. `core/compiler/service.py` & `core/compiler/assembler.py`
* **Demostración por Código Fuente:**
  En `apps/compiler/__main__.py` (`AssemblerWorkerDaemon._process_assembly_task()`), el worker extrae las proyecciones directamente de `MaterializedPlaneRepository.get_assemblable_chunks()` y reconstruye la lista `valid_chunks: List[RenderUnit]` manualmente en un bucle for. **Ni `CompilationService` ni `DocumentAssembler` son invocados**.
* **Impacto Arquitectónico:** **[P0 - CRÍTICO]**. Las políticas institucionales de tolerancia a fallos (`AssemblyPolicy`), las reglas de degradación por ratio (`tolerance_ratio`), la verificación de firmas SHA-256 (`get_verified_payload`) y la validación de secuencias estrictas quedan completamente anuladas en el flujo de producción en segundo plano.

---

### P6-H02: Condición de Carrera en I/O y Inseguridad Concurrente en `DockerRunner` [DEMOSTRADO]
* **Ubicación:** `apps/compiler/docker_runner.py`
* **Demostración por Código Fuente:**
  En `DockerRunner.compile()`:
  ```python
  crash_log_path = os.path.join(os.getcwd(), "tectonic_crash.log")
  with open(crash_log_path, "w", encoding="utf-8") as f:
      f.write(result.stderr)
  ...
  final_path = os.path.join(os.getcwd(), output_filename)
  shutil.copy(compiled_pdf_path, final_path)
  ```
  El ejecutor escribe el log de fallos `tectonic_crash.log` y copia el archivo PDF final en el directorio de trabajo actual del proceso (`os.getcwd()`).
* **Impacto ArquITECTÓNICO:** **[P0 - CRÍTICO]**. Si múltiples instancias de `AssemblerWorkerDaemon` o procesos concurrentes ejecutan compilaciones simultáneas sobre el mismo CWD, se producen **sobrescrituras de archivos, corrupción de PDFs finales e interconexión cruzada de logs de error (*Race Conditions*)**.

---

### P6-H03: Incongruencia de Nombre y Falta de Aislamiento de Sandbox ("DockerRunner" Falso) [DEMOSTRADO]
* **Ubicación:** `apps/compiler/docker_runner.py`
* **Demostración por Código Fuente:**
  A pesar de llamarse `DockerRunner`, la implementación ejecuta directamente el binario del host vía subproceso:
  ```python
  cmd = ["tectonic", "--untrusted", "doc.tex"]
  result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=120, cwd=tmp)
  ```
* **Impacto ArquITECTÓNICO:** **[P1 - ALTO]**. Desalineación semántica y riesgo de seguridad. El sistema no ejecuta en un contenedor Docker efervescente aislado, exponiendo el entorno host a vulnerabilidades de compilación si se inyecta código TeX malicioso o recursos locales no autorizados.

---

### P6-H04: Deuda Técnica Reconocida en Escapador TeX Ciego al Contexto (`LatexEscaper`) [DEMOSTRADO]
* **Ubicación:** `core/compiler/rendering/implementations.py` (`LatexEscaper`)
* **Demostración por Código Fuente:**
  El propio código fuente incluye una advertencia explícita:
  ```python
  class LatexEscaper:
      """
      DEUDA TÉCNICA (MVP): Este escaper es ciego al contexto. 
      TODO: Migrar a un Lexer AST-aware (ej. pylatexenc) o inyectar contexto de escape.
      """
      _ESCAPE_MAP = {
          '\\': r'\textbackslash{}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
          '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}'
      }
  ```
* **Impacto ArquITECTÓNICO:** **[P1 - ALTO]**. Si un bloque clasificado como texto es procesado por `TextRenderStrategy`, el escapador sustituirá ciegamente caracteres matemáticos legítimos (`_`, `^`, `{`, `}`), corrompiendo fórmulas en línea e interrumpiendo el compilador Tectonic.

---

### P6-H05: Excelencia Técnica SRE en la Capa de Serialización Atómica (`ast_json.py`) [DEMOSTRADO]
* **Ubicación:** `infra/serialization/ast_json.py` (`write_ast_json_atomic()`)
* **Demostración por Código Fuente:**
  `write_ast_json_atomic()` implementa el patrón de persistencia atómica impecable:
  ```python
  with tempfile.NamedTemporaryFile("w", dir=target_dir, delete=False, encoding="utf-8") as tf:
      temp_path = pathlib.Path(tf.name)
      tf.write(content)
      tf.flush()
      try:
          os.fsync(tf.fileno())
      except (AttributeError, OSError):
          pass
  temp_path.rename(target_path)
  ```
* **Veredicto Metodológico:** **SOTA / APROBADO**. Vaciado físico de búfer del SO (`os.fsync`) y reemplazo atómico de punteros de inode (`rename`), garantizando inmunidad absoluta contra corrupción por cortes de energía o caídas del proceso.

---

### P6-H06: Asunción Rígida de Secuenciación Base 1 en `DocumentAssembler` [DEMOSTRADO]
* **Ubicación:** `core/compiler/assembler.py` (`_validate_sequence()`)
* **Demostración por Código Fuente:**
  In `_validate_sequence()`:
  ```python
  expected_index = 1
  for outcome in outcomes:
      if outcome.chunk_index != expected_index:
          raise IncompleteDocumentError(...)
      expected_index += 1
  ```
* **Impacto ArquITECTÓNICO:** **[P2 - MEDIO]**. Si un chunker emite secuencias con índice base 0 (`0, 1, 2...`), `DocumentAssembler` rechazará inmediatamente el documento lanzando `IncompleteDocumentError` en el primer fragmento, a pesar de estar completo.

---

## 3. TRAZABILIDAD Y FLUJO DE DATOS OPERACIONAL (RUNTIME VS. TEORÍA)

```text
==================================================================================================
                 TRAZABILIDAD DE ENSAMBLADO Y COMPILACIÓN (CÓDIGO VERIFICADO)
==================================================================================================

  [MaterializedPlaneRepository]
            │
            ▼
  [AssemblerWorkerDaemon._process_assembly_task()] <--- [BYPASS DEL CORE]
            │
            ├──► Recolección ad-hoc: text_map = {record.node_id: record.normalized_response}
            ├──► Invocación directa a TexBuilder
            │
            ▼
  [TexBuilder.build(valid_chunks)]
            │
            ├──► DynamicDocumentStructure.begin_document() (Preamble)
            ├──► RenderContext.render_unit()
            └──► DynamicDocumentStructure.end_document()
            │
            ▼
  [DockerRunner.compile(tex_content)] <--- [INSEGURIDAD CONCURRENTE]
            │
            ├──► Purga de caracteres de control y entidades HTML
            ├──► tempfile.TemporaryDirectory()
            ├──► subprocess.run(["tectonic", "--untrusted", "doc.tex"])
            │
            ├──► (Fallo TeX?) ──► LogParser.parse(stderr) ──► FailDocumentCommand
            │
            └──► (Éxito PDF?) ──► shutil.copy(tmp/doc.pdf, CWD/output.pdf) <--- [RACE CONDITION]
                                        │
                                        ▼
                               CompleteDocumentCommand
```

---

## 4. TAXONOMÍA Y MATRIZ DE COMPONENTES DEL BLOQUE P6

| Componente / Módulo | Categoría ArquITECTÓNICA | Severidad | Diagnóstico Forense Clave | Disposición Hito 0.5 |
| :--- | :--- | :---: | :--- | :--- |
| `infra/serialization/ast_json.py` | Serialization Layer | **Cero** | Escritura atómica SRE certificada (`fsync` + `rename`). | **CONSERVAR** |
| `apps/compiler/log_parser.py` | Log Parsing | **Cero** | Clasificación determinista de errores TeX/Tectonic mediante Regex. | **CONSERVAR** |
| `apps/compiler/tex_builder.py` | TeX Generation | **Cero** | Excelente desacoplamiento e inversión de control vía `RenderContext`. | **CONSERVAR** |
| `apps/compiler/__main__.py` | Compiler Daemon | **P0 (Crítico)** | Salta `CompilationService` y `DocumentAssembler`; mapeo ad-hoc. | **REFACTORIZAR A SERVICE** |
| `apps/compiler/docker_runner.py` | Execution Sandbox | **P0 (Crítico)** | Race conditions por I/O en `getcwd()` e invocación host no aislada. | **AISLAR I/O Y REESTRUCTURAR** |
| `core/compiler/service.py` | Core Compilation | **P0 (Crítico)** | Módulo orquestador Clean/DDD zombi en el daemon de producción. | **ENLAZAR EN DAEMON** |
| `core/compiler/rendering/implementations.py`| Rendering Engine | **P1 (Alto)** | `LatexEscaper` ciego al contexto TeX (reemplazo ciego). | **MIGRAR A ESCAPER AST-AWARE** |
| `core/compiler/assembler.py` | Assembler Core | **P2 (Medio)** | Asunción rígida de base 1 en secuencia de Chunks (`expected_index`).| **FLEXIBILIZAR SECUENCIA** |

---

## 5. MARCO NORMATIVO Y REGLAS DE REMEDIACIÓN FUTURA (P6-R01 A P6-R05)

Queda **estrictamente prohibida la modificación de código** durante la Fase 0. Las siguientes normativas forman el mandato técnico ineludible de remediación para el **Hito 0.5** y la **Fase 17_BIS**:

* **P6-R01 (Inyección Obligatoria de `CompilationService` en Daemon - P0):** Refactorizar `AssemblerWorkerDaemon._process_assembly_task()` en `apps/compiler/__main__.py` para que delegue la compilación exclusivamente a `CompilationService.compile_document()`, garantizando la ejecución de `DocumentAssembler` y sus políticas de tolerancia (`AssemblyPolicy`).
* **P6-R02 (Aislamiento Anticolisión de I/O en Compilador - P0):** Eliminar el uso de `os.getcwd()` en `apps/compiler/docker_runner.py`. Los PDFs finales y los logs de crash deben escribirse en directorios temporales aislados por `job_id` o en la ruta de almacenamiento configurada para evitar condiciones de carrera entre workers concurrentes.
* **P6-R03 (Sustitución de Escapeo Ciego TeX - P1):** Reemplazar `LatexEscaper` en `core/compiler/rendering/implementations.py` por un escapador consciente del contexto o AST-aware, impidiendo que bloques de texto escapen delimitadores y macros TeX válidas.
* **P6-R04 (Flexibilización de Índice de Secuencia en Assembler - P2):** Modificar `DocumentAssembler._validate_sequence()` para determinar dinámicamente el índice inicial del primer chunk (`start_index = outcomes[0].chunk_index`), permitiendo la validación de secuencias base 0 o base 1 indistintamente.
* **P6-R05 (Veracidad de Nombres e Integración Sandbox - P1):** Renombrar `DockerRunner` a `TectonicHostRunner` o encapsular la invocación de `Tectonic` dentro de un contenedor efervescente de Docker para reflejar con veracidad su nivel de aislamiento.

---

## 6. EVALUACIÓN DE CONFIABILIDAD OPERACIONAL Y VEREDICTO DE CIERRE

### 6.1 DIAGNÓSTICO DE CONFIABILIDAD OPERACIONAL
1. **Capa de Serialización de Disco:** **EXCEPCIONAL Y SOTA.** `infra/serialization/ast_json.py` cumple con los estándares más estrictos de ingeniería de confiabilidad (SRE) mediante escrituras intermedias, vaciado físico a disco (`os.fsync`) y reemplazo atómico.
2. **Plano de Compilación y Ensamblado en Producción:** **INCOMPLETO Y VULNERABLE.** El daemon de compilación se salta la capa formal de dominio, realiza un re-ensamblado ad-hoc y ejecuta subprocesos con riesgo de colisión de archivos en entornos multihilo o multiworker.

---

### 6.2 DECISIÓN FINAL DEL SUB-HITO 0.4.5-P6

The audit for **Block P6 (Assembly $\rightarrow$ Serialization $\rightarrow$ Compiler $\rightarrow$ Artifact)** is hereby declared **CLOSED**.

```text
====================================================================================
                  ESTADO DE AUDITORÍA: SUB-HITO 0.4.5-P6
====================================================================================
  Audit Status             | CLOSED (Auditoría Forense Finalizada por Código Fuente)
  Code Remediation         | DEFERRED (Diferido a Hito 0.5)
  Production Certification | NOT GRANTED (CompilationService bypasseado; Race conditions en I/O)
  Remediation Backlog      | OPEN (Reglas P6-R01 a P6-R05 Registradas)
====================================================================================
```

**Bitácora de Gobernanza:**
> *"Se da por concluida la auditoría forense del Bloque P6 tras la inspección del código fuente. Se certifica la excelencia técnica de la capa de serialización atómica (infra/serialization/ast_json.py). Sin embargo, se decreta el rechazo arquitectónico del plano de compilación en producción debido a que AssemblerWorkerDaemon bypassea el núcleo del compilador (CompilationService y DocumentAssembler), anulando las políticas de tolerancia y creando condiciones de carrera por I/O sobre os.getcwd() en DockerRunner. Queda estrictamente prohibido mutar código. Todas las reglas de remediación quedan congeladas para el Hito 0.5."*
```