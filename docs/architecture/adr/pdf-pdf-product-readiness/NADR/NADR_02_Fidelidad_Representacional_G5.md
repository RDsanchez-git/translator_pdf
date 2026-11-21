# NADR-FPPPR-02: Fidelidad de Representación del Contenido Protegido y de la Jerarquía Documental en G5

**FROZEN v1.0.0 — aprobado integralmente por el Architecture Board el 2026-11-20; congelamiento documental autorizado.**

## 1. METADATA

- **Decision ID:** `NADR-FPPPR-02` — identificador ratificado por el Architecture Board.
- **Título:** Fidelidad de Representación del Contenido Protegido y de la Jerarquía Documental en G5.
- **Clase de Decisión:** `DATA / STRUCTURAL`.
- **Nivel de Cumplimiento:** MANDATORY.
- **Versión:** `1.0.0` — primera versión FROZEN; nueve reglas RFC 2119 aprobadas sin alteraciones desde DRAFT v0.3.0.
- **Ciclo de Vida:** FROZEN.
- **Fecha de Aprobación Integral:** 2026-11-20; decisión expresa comunicada por el owner en nombre del Architecture Board sobre PR #77, HEAD `a0421fc289fdee2c3d0374a9e2dba0ec6c6b1de8` (DRAFT v0.3.0).
- **Fecha de Congelamiento Documental:** 2026-11-20; autorizado en la misma comunicación.
- **Procedencia de Autoridad:** Comunicación directa del owner en esta conversación; no se presupone acta externa, firma ni review formal de GitHub. El merge del PR #77 requiere autorización separada.
- **Vigente Desde:** Etapa normativa PPPR — 2026-11-20, tras aprobación integral del Board; orienta el futuro Execution Plan PPPR sin autorizar implementación ni certificación científica.
- **Autoridad:** Architecture Board.
- **Responsable Técnico:** Staff Engineering / G5 — rol ratificado por el Architecture Board; no se designa una persona.
- **Capacidad Arquitectónica:** `CAP-PPPR-02` (código ratificado) — Fidelidad de representación del contenido protegido y de la jerarquía documental durante la reconstrucción.
- **Evidencia Forense:** `GAP-0.6-01/02`; `E-0.6-012/013/014/025/026`; `E-0.3-013/018/019`; `PROJECT_SCOPE.md` §§2/4.
- **Referencias Cruzadas:**
  - **Depende de:** `ADR_PPPR_MASTER.md` FROZEN, especialmente DC-05 y DC-06.
  - **Influencia prevista:** futuro `PHASE_PPPR_EXECUTION_PLAN.md`, sujeto a autorización.
  - **Fronteras compatibles:** `NADR-F17BIS-03/05/09`, NADR F18 aplicables y `NADR-FPPPR-01` FROZEN, sin presuponer nuevas dependencias recíprocas.
  - **Referencia no vinculante:** `NADR-F17BIS-06` PROPOSED.
  - **Conflictúa con:** interpretar contenido literal como instrucciones, descartar jerarquía válida y declarar fidelidad representacional no acreditada.
  - **Reemplaza a:** N/A.

Este NADR utiliza la convención excepcional PPPR autorizada. No constituye una fase numerada del ROADMAP. Su aprobación integral y FROZEN son documentales y no autorizan por sí solos el merge del PR #77, ejecución de pruebas, implementación ni certificación del producto.

## 2. ARCHITECTURE RISK SCORE

Riesgo arquitectónico de carecer de reglas verificables específicas para la fidelidad de representación en G5. No representa incidentes físicos observados.

| Dimensión | Puntaje | Justificación |
|---|---:|---|
| Operacional | 4/5 | Puede emitirse un artefacto técnicamente válido con contenido literal o jerarquía mal representados. |
| Mantenibilidad | 3/5 | La confusión entre literal, marcado válido y estructura dificulta preservar contratos entre etapas. |
| Recuperabilidad | 3/5 | La pérdida de procedencia o estructura dificulta atribuir el origen de una degradación. |
| Seguridad | 2/5 | Riesgo de interpretación no deseada del contenido como marcado; no se demuestra explotación. |
| Financiero | 2/5 | Riesgo de reensamblado y revisión adicional, sin impacto económico medido. |
| **Total** | **14/25** | **S2 — ALTO, ratificado por el Board** |

- **Total Score:** `14/25`.
- **Severidad:** `S2` — ALTO, ratificado por el Architecture Board (14/25).

## 3. DECISIÓN EJECUTIVA

**La reconstrucción documental DEBERÁ preservar de manera verificable el significado representacional del contenido protegido, la estructura legítimamente identificada y la función y jerarquía válidas de los elementos recibidos, sin introducir interpretaciones indebidas ni presentar pérdidas o incertidumbres como fidelidad acreditada.**

En consecuencia:

- El contenido literal y el marcado legítimamente activo mantienen tratamientos diferenciados.
- Los niveles jerárquicos válidos recibidos permanecen distinguibles en el documento reconstruido.
- La información faltante o incierta no se inventa ni se declara preservada.
- La reconstrucción no asume responsabilidades de traducción ni certificación científica.

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La reconstrucción del PDF transforma contenido estructurado en una representación física.

Esa transformación debe proteger dos propiedades vinculadas: la interpretación correcta del contenido tipado y la conservación de las relaciones estructurales relevantes.

Se identifican tres riesgos:

1. **Confusión de interpretación:** contenido que debe permanecer literal adquiere un significado sintáctico activo no autorizado.
2. **Pérdida jerárquica:** diferencias conocidas entre niveles de encabezado desaparecen durante la representación.
3. **Falsa fidelidad:** una pérdida introducida durante la transformación, o una propiedad nunca recibida desde upstream, se presenta como preservada.

La capacidad requerida no equivale a identidad semántica del AST, validación científica del PDF ni control operacional del compilador.

### 4.2 Manifestación concreta identificada por la auditoría

**GAP-0.6-01 / E-0.6-025 — P1 LOCAL OPEN.** La ruta G5 admite CODE/TABLE mediante `PassthroughRenderStrategy` y concatena contenido crudo en `TexBuilder`. Caracteres como `_`, `%` y `&` pueden adquirir significado sintáctico en un contexto que requiere conservación literal. No se ejecutó una compilación física que demuestre un fallo real.

**GAP-0.6-02 / E-0.6-026 — P1 LOCAL OPEN.** El AST admite niveles H1/H2/H3 y registra profundidad, pero `DefaultRenderUnitMapper` no transporta esa diferenciación; HEADING y PARAGRAPH comparten estrategia de representación. No se acredita preservación de niveles en la salida.

**E-0.6-012 — P2, límite de evidencia.** `TextRenderStrategy::render` escapa prosa y conserva spans explícitos de matemática; testigos B02.4 examinan delimitadores. Esto sustenta la necesidad de distinguir regiones matemáticas legítimamente identificadas del contenido literal, pero no prueba semántica STEM ni certifica un PDF físico.

**E-0.3-013/018/019 — P2.** La ruta upstream presenta divergencia entre la estrategia declarada de traducción de HEADING y su clasificación observada como PRESERVE; también existe aplanamiento jerárquico anterior a G5. La reconstrucción no puede afirmar haber preservado información que no recibió.

**NADR-F17BIS-09 — FROZEN.** §5.2 cubre aislamiento de artefactos de compilación en su ámbito compatible, no preservación semántica de CODE/TABLE o HEADING.

**NADR-F17BIS-06 — PROPOSED.** Sus reglas sobre TeX y ensamblado no constituyen obligación FROZEN. `GAP-0.6-03` permanece histórico y retirado; `E-0.6-027` conserva su naturaleza P2.

**ADR Maestro PPPR — FROZEN.** DC-05 exige traducción de encabezados naturales preservando función y jerarquía. DC-06 exige preservar contenido literal frente a sintaxis legítima. Ambas decisiones constitucionales ya están resueltas; el presente candidato se limita a la obligación verificable residual de reconstrucción.

## 5. REGLAS NORMATIVAS (RFC 2119)

**Reglas normativas aprobadas por el Architecture Board; vigentes para esta capacidad desde FROZEN v1.0.0.**

### 5.1 Protección de la interpretación del contenido

1. La reconstrucción de elementos documentales **MUST** respetar la clasificación válida y trazable que distingue contenido literal protegido, contenido estructurado legítimamente identificado y función semántica de cada elemento. La reconstrucción **MUST NOT** alterar silenciosamente esa clasificación.

2. Las regiones identificadas por contrato como contenido literal protegido, incluidos bloques CODE y contenido literal de TABLE, **MUST** preservar su contenido lógico y sus caracteres significativos en el resultado representado. Las transformaciones necesarias para su codificación física **MAY** emplearse cuando conserven ese contenido, pero la presencia de caracteres sintácticos especiales **MUST NOT** convertirlo involuntariamente en instrucciones activas.

3. Las regiones matemáticas o de marcado TeX legítimamente identificadas como activas por el contrato de entrada aplicable **MUST** conservar la función representacional que dicho contrato reconoce y **MUST NOT** ser tratadas como texto literal mediante transformaciones indiferenciadas. La semejanza textual con una instrucción o macro **MUST NOT**, por sí sola, conferir autoridad para interpretarla como marcado activo.

4. Cuando un elemento contenga regiones literales y regiones estructuradas válidamente diferenciadas, la reconstrucción **MUST** respetar sus límites y clasificación; **MUST NOT** aplicar una interpretación uniforme que elimine esa distinción. Esta regla es condicional y no presupone que toda entrada contenga regiones mixtas.

### 5.2 Fidelidad de jerarquía documental

5. Los encabezados **MUST** conservar en la reconstrucción su función documental y el nivel jerárquico válido recibido. Cuando el contrato de entrada distinga niveles, la representación final **MUST** mantener esa distinción estructuralmente reconocible, sin exigir un estilo gráfico, macro o diseño físico específico.

6. Cuando el nivel jerárquico necesario sea desconocido, inválido o no esté acreditado en la entrada, la reconstrucción **MUST NOT** inventar silenciosamente un nivel ni afirmar que preservó fielmente la jerarquía fuente. Esa limitación **MUST** permanecer identificable y **MUST NOT** presentarse como cumplimiento de la propiedad ausente.

7. La reconstrucción **MUST** respetar el contenido de salida de un encabezado seleccionado mediante el contrato de generación aplicable y **MUST NOT** sustituirlo silenciosamente por otro texto. La reconstrucción **MUST NOT** presentarse como mecanismo que traduce, corrige o certifica la calidad lingüística de ese contenido. La falta de traducción requerida permanece bajo la responsabilidad upstream y la aceptación científica correspondiente.

### 5.3 Pérdidas y trazabilidad representacional

8. Cuando la reconstrucción no pueda preservar una propiedad exigida por el contrato de entrada, la pérdida o limitación **MUST** quedar identificada de forma atribuible. El resultado **MUST NOT** presentarse como representacionalmente íntegro ni como producto final conforme mientras persista ese incumplimiento. Un artefacto parcial o diagnóstico **MAY** conservarse únicamente bajo los límites de DC-12, sin presumir que exista una ruta productiva autorizada para publicarlo como conforme.

9. La correspondencia verificable entre elementos tipados recibidos y elementos reconstruidos **MUST** permitir comprobar las propiedades representacionales exigidas, incluidos contenido protegido, función documental y niveles jerárquicos conocidos. Esa comprobación **MUST NOT** presentarse como certificación científica integral del PDF final, cuya legitimidad se rige por `NADR-FPPPR-01`.

## 6. CONSECUENCIAS ARQUITECTÓNICAS

- El contenido literal y el marcado legítimo permanecen separados por contratos comprobables.
- La codificación física puede variar sin alterar el contenido lógico protegido.
- Los niveles de jerarquía válidos recibidos no desaparecen silenciosamente en el resultado representado.
- La reconstrucción no inventa información estructural faltante ni promete corregir defectos upstream.
- Las pérdidas de propiedades requeridas se vuelven atribuibles y bloquean afirmar conformidad final mientras persistan, sin habilitar productos DEGRADED conformes.
- La preservación representacional permanece separada de la certificación científica y de la autoridad operacional.

## 7. VERIFICACIÓN Y VALIDACIÓN

**Estado: NOT_RUN.** Los falsadores son propuestas para ejecución posterior autorizada.

**Verification — estática/mecánica**

- Comprobar que el contrato de entrada mantiene la distinción entre contenido literal y regiones matemáticas o marcado TeX legítimamente acreditados como activos; la semejanza textual no basta.
- Comprobar que CODE y regiones literales de TABLE no pierden su clasificación antes de su representación.
- Comprobar que niveles HEADING válidos llegan a la frontera de representación y que niveles no acreditados no se convierten en niveles supuestamente fieles.
- Comprobar la separación entre responsabilidad upstream de traducción y responsabilidad de reconstrucción.
- Comprobar que una propiedad obligatoria perdida queda atribuida al alcance afectado y bloquea la presentación del resultado como representacionalmente íntegro o producto final conforme, incluso si el PDF compila o está marcado `NOT_CERTIFIED`.

**Validation — dinámica/comportamental**

| Falsador propuesto | Resultado exigido |
|---|---|
| CODE literal con `_`, `%`, `&` | Contenido lógico conservado; sin interpretación como instrucciones. |
| Región literal de TABLE con caracteres especiales | Contenido protegido sin alteración involuntaria. |
| Región matemática/TeX activa acreditada por contrato de entrada | Función representacional conservada; no degradarla a texto literal por tratamiento indiscriminado. |
| Texto literal semejante a una macro, sin autoridad de marcado activo | No ejecutarlo como marcado activo por semejanza textual. |
| Elemento con regiones mixtas válidamente clasificadas | Se respetan límites y tratamientos correspondientes; no presumir que todo elemento es mixto. |
| HEADING H1 y H2 válidos con texto idéntico | Diferencia jerárquica reconocible en el resultado. |
| HEADING con nivel no acreditado | No se inventa nivel ni se afirma preservación de la jerarquía desconocida. |
| Contenido EN→ES seleccionado para HEADING | Se representa el contenido recibido; G5 no lo retraduce ni certifica. |
| Contenido de HEADING no traducido upstream | G5 no se presenta como solución de traducción ni acredita por sí sola cumplimiento EN→ES. |
| Pérdida de CODE/TABLE o jerarquía obligatoria en PDF compilable o marcado `NOT_CERTIFIED` | Pérdida atribuible, sin presentar el resultado como íntegro ni producto final conforme; el estado de compilación o certificación no prueba preservación. |
| Artefacto parcial o diagnóstico ante pérdida representacional | Conservación solo bajo límites de DC-12; ninguna ruta de publicación conforme se presume autorizada. |

Los falsadores de representación pueden diseñarse mediante entradas sintéticas sin corpus privado ni servicio comercial. La validación científica integral del PDF final requiere evidencia y criterios autorizados propios. Ninguno de los escenarios precedentes ha sido ejecutado por este NADR.

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
|---|---|
| `ADR_PPPR_MASTER.md` FROZEN | **Autoridad superior:** DC-05/06 establecen traducción de encabezados, preservación jerárquica y protección de contenido literal frente a marcado legítimo. |
| `HITO_PPPR.0.3` FROZEN | **Evidencia upstream:** E-0.3-013/018/019 sobre estrategia HEADING y procedencia de niveles. |
| `HITO_PPPR.0.6` FROZEN | **Evidencia principal:** GAP-0.6-01/02 y E-0.6-012/013/014/025/026. |
| `NADR-F17BIS-03` FROZEN | **Delimitación de capacidad:** firma e identidad semántica del AST, no representación del PDF reconstruido. |
| `NADR-F17BIS-05` FROZEN | **Delimitación de capacidad:** resolución de contexto, no representación final de niveles jerárquicos. |
| `NADR-F17BIS-06` PROPOSED | **Contraste no vinculante:** no se importa su obligación sobre sintaxis ni se reactiva GAP-0.6-03. |
| `NADR-F17BIS-09` FROZEN | **Ámbito compatible:** aislamiento de compilación según §5.2, distinto de preservación representacional. |
| `NADR-F18-03/04/05` FROZEN | **Autoridad operacional preservada:** efectos inciertos, persistencia y recuperación en sus ámbitos. |
| `NADR-FPPPR-01` FROZEN | **Frontera complementaria:** gobierna las afirmaciones científicas sobre el PDF final, no la transformación interna de su contenido. |
| Futuro `PHASE_PPPR_EXECUTION_PLAN.md` | **Destino de materialización:** mecanismos y pruebas autorizados posteriormente, sin fuerza para crear normas nuevas. |

Las referencias de ámbito o contraste no se declaran dependencias normativas recíprocas. Una relación directa adicional necesitaría acreditación y tratamiento conforme a `4_METH_NADR.md` §8. No se modifican documentos FROZEN existentes.

## 9. FRONTERA NORMATIVA (QUÉ NO GOBIERNA ESTE NADR)

- **No gobierna** extracción OCR, perfilado geométrico ni la identificación original de páginas.
- **No gobierna** firmas AST, canonización Unicode ni identidad de generación traducida.
- **No gobierna** la política de traducción EN→ES, el enrutamiento de inferencia o la generación lingüística de HEADING.
- **No gobierna** la identidad, legitimidad o autoridad de los oráculos científicos del PDF final, reguladas por el ADR Maestro y `NADR-FPPPR-01`.
- **No gobierna** autoridad de ejecución, recuperación de efectos inciertos, persistencia ni aislamiento de artefactos cubiertos por contratos FROZEN aplicables.
- **No autoriza** interpretar como marcado activo macros textuales cuya legitimidad no esté acreditada ni reactivar `GAP-0.6-03`.
- **No impone** equivalencia visual exacta con el PDF fuente, estilos determinados, algoritmos de render, lenguajes de marcado, bibliotecas, clases ni comandos.
- **No prescribe** tareas, Definition of Done, despliegue, proveedores o métricas de aceptación científica.
- **No autoriza** implementación, evaluaciones comerciales, uso de corpus privados ni merge.

**Nota de gobernanza:** las nueve reglas constituyen el contrato normativo FROZEN de esta capacidad. La aprobación integral no repara los GAP forenses, no constituye certificación científica del producto, no acredita pruebas ejecutadas y no autoriza implementación ni merge del PR #77; estas acciones permanecen sometidas a sus gates y autorizaciones propias.
