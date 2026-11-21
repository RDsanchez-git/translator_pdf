# NADR-FPPPR-04 — Integridad de Procedencia Física y Geometría Verificable del Documento

**FROZEN v1.0.0 — aprobado integralmente por el Architecture Board el 2026-11-21 sobre DRAFT v0.3.0 (HEAD `c07580b4c122bb4892cf48f41ce7b555ab178005`); congelamiento documental autorizado.**

## 1. METADATA

- **Decision ID:** `NADR-FPPPR-04` — identificador ratificado por el Architecture Board.
- **Título:** Integridad de Procedencia Física y Geometría Verificable del Documento.
- **Clase de Decisión:** `DATA / STRUCTURAL`.
- **Nivel de Cumplimiento:** `MANDATORY`.
- **Versión:** `1.0.0` — primera versión FROZEN; diez reglas RFC 2119 aprobadas íntegramente y sin alteraciones desde DRAFT v0.3.0.
- **Ciclo de Vida:** `FROZEN`.
- **Fecha de Aprobación Integral:** 2026-11-21; decisión comunicada por el owner en nombre del Architecture Board sobre PR #79, HEAD `c07580b4c122bb4892cf48f41ce7b555ab178005` (DRAFT v0.3.0).
- **Fecha de Congelamiento Documental:** 2026-11-21; autorizado en la misma comunicación.
- **Procedencia de Autoridad:** Comunicación directa del owner en esta conversación; no se presupone acta externa, firma ni review formal de GitHub. En instrucción posterior separada, el owner autorizó el merge del PR #79 exclusivamente hacia `pdf-pdf-product-readiness`, sin incluir `main` ni PR #66.
- **Vigente Desde:** Etapa normativa PPPR — 2026-11-21, tras aprobación integral; toda materialización posterior queda condicionada al Execution Plan y autorizaciones pertinentes.
- **Autoridad:** Architecture Board.
- **Responsable Técnico:** `Staff Engineering / Ingesta y Perfilado` — rol ratificado por el Architecture Board; no se designa persona.
- **Capacidad Arquitectónica:** `CAP-PPPR-04` — código ratificado por el Architecture Board. Preservación y utilización verificable de procedencia por página, referencias geométricas y dimensiones físicas entre la extracción, la representación estructural y sus consumidores.
- **Evidencia Forense:** `GAP-0.2-01/02`; `E-0.2-011/012/013/017/020`; `E-0.6-010/028`; `E-0.9-006/007`; `PROJECT_SCOPE.md` §§2/4; `ENGINEERING_PRINCIPLES.md` §§III–IV.
- **Referencias Cruzadas:**
  - **Depende de:** `ADR_PPPR_MASTER.md` FROZEN, especialmente §5 (preservación y linaje) y §8.1 (suficiencia normativa).
  - **Influencia prevista:** futuro `PHASE_PPPR_EXECUTION_PLAN.md`; materialización sujeta a su aprobación y al gate de suficiencia normativa.
  - **Contratos compatibles por ámbito:** `NADR-F17BIS-01/02` FROZEN y `NADR-FPPPR-02` FROZEN.
  - **Referencia de contraste:** `NADR-F17BIS-04`, cuyo estado publicado es APPROVED con formalización editorial FROZEN pendiente.
  - **Conflictúa con:** atribución ficticia de páginas; normalización geométrica con dimensiones no acreditadas; pérdida silenciosa de procedencia multipágina; muestreos presentados como físicamente acotados sin garantía de ello.
  - **Reemplaza a:** `N/A`.

El Architecture Board aprobó integralmente las diez reglas, el identificador, la capacidad, el responsable como rol, el riesgo 13/25 — S2, las fronteras y las relaciones normativas, según decisión comunicada por el owner sobre el HEAD revisado. Se autorizó el FROZEN v1.0.0 y, en instrucción posterior separada, el merge **solo** hacia `pdf-pdf-product-readiness`. No se autorizan implementación, pruebas físicas ni certificación científica.

PPPR continúa siendo una iniciativa transversal de gobernanza, no una fase numerada del ROADMAP.

## 2. ARCHITECTURE RISK SCORE

Evaluación ratificada por el Architecture Board del riesgo arquitectónico de interpretar geometrías físicas sin procedencia y escala acreditables.

| **Dimensión**   | **Puntaje** | **Justificación**                                                                                                               |
| --------------- | ----------: | ------------------------------------------------------------------------------------------------------------------------------- |
| Operacional     |         4/5 | Un consumidor puede tomar decisiones de perfilado o reconstrucción utilizando geometrías que no corresponden a la página real.  |
| Mantenibilidad  |         3/5 | La pérdida de significado entre representación y consumidor dificulta sustituir adaptadores sin introducir nuevas divergencias. |
| Recuperabilidad |         3/5 | Una decisión geométrica incorrecta puede ser difícil de atribuir y reproducir si no conserva la procedencia utilizada.          |
| Seguridad       |         1/5 | No se acredita explotación, exposición de datos ni una vulnerabilidad de seguridad directamente vinculada a estos GAP.          |
| Financiero      |         2/5 | El muestreo mal acotado puede generar procesamiento adicional; no se dispone de mediciones de coste o impacto financiero.       |
| **Total**       |   **13/25** | **S2 — ALTO, ratificado por el Architecture Board**                                                                                                      |

- **Total Score:** `13/25`.
- **Severidad:** `S2` — ratificada por el Architecture Board.
- **Límite probatorio:** el riesgo deriva de incumplimientos estructurales demostrados, no de una tasa observada de errores en un corpus científico.

## 3. DECISIÓN EJECUTIVA

**Toda transformación o decisión documental que dependa de información física de páginas DEBERÁ utilizar procedencia, geometría y dimensiones de referencia verificables y coherentes con la fuente, conservar las relaciones necesarias cuando el contenido abarque varias páginas e impedir que referencias ausentes, ambiguas o supuestas sean presentadas como información geométrica acreditada.**

En consecuencia:

- La procedencia física debe conservar el vínculo entre regiones utilizadas y páginas de origen.
- Las geometrías absolutas y relativas no son intercambiables sin una transformación acreditada.
- Los nodos multipágina son representaciones legítimas, no anomalías que deban colapsarse.
- Los muestreos declarados por páginas deben respetar su alcance físico.
- Las propiedades desconocidas no pueden transformarse silenciosamente en certezas.
- La verificación geométrica no constituye certificación científica del PDF final.

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

El pipeline transforma contenido físico de un documento PDF en una representación estructurada que posteriormente utilizan el perfilado documental y el ensamblado.

Durante esas transformaciones, una geometría puede cambiar de representación, combinarse con otras regiones o ser consumida para tomar decisiones sobre columnas, posición o tamaño de figuras.

La validez de esas decisiones depende de información que no es exclusivamente numérica: la página física a la que pertenece una región, el espacio de coordenadas utilizado y las dimensiones que permiten interpretar su escala.

Un valor derivado puede ser aritméticamente válido y, aun así, no representar correctamente la posición del elemento dentro de su página fuente.

La normalización trans-página introduce una condición adicional: un mismo nodo lógico puede contener regiones provenientes de páginas físicas diferentes. En consecuencia, no es correcto presuponer que la identidad física del nodo se reduzca siempre a una sola página o a una sola geometría representativa.

Esta capacidad no exige reproducir visualmente el PDF fuente con exactitud absoluta; exige que la información física empleada para adoptar decisiones tenga un significado verificable.

### 4.2 Manifestación concreta identificada por la auditoría

**GAP-0.2-01 — E-0.2-011; P1 LOCAL OPEN.**

La representación AST utiliza `NodeMetadata.pages: List[int]`. El adaptador de perfilado consulta `metadata.page_number`, atributo no definido en dicho modelo, y emplea `0` como respaldo. El valor alimenta `FirstPagesSamplingPolicy`, que declara una carga limitada a primeras páginas físicas.

La auditoría demuestra que, en la ruta inspeccionada, el muestreo puede procesar nodos posteriores a la muestra declarada porque no distingue las identidades de página correspondientes.

No se midió consumo adicional de CPU ni impacto científico.

**GAP-0.2-02 — E-0.2-012; P1 LOCAL OPEN.**

El proveedor conoce dimensiones físicas de página y genera BBox absolutos. El AST transporta esas geometrías, pero la proyección hacia el perfilador no conserva una referencia suficiente al ancho físico pertinente.

`NodeGeometryAdapter` utiliza un ancho de respaldo de `612.0` puntos. `HeuristicLayoutDetector` consume el cociente resultante como posición relativa.

Ejemplo analítico de la auditoría:

- Página de 300 puntos de ancho.
- Centro horizontal de un elemento: 210 puntos.
- Posición relativa correcta: `210 / 300 = 0.70`.
- Posición emitida con respaldo: `210 / 612 ≈ 0.343`.

Ese cambio puede invertir la clasificación espacial de un elemento. No demuestra frecuencia de fallo en documentos reales.

**E-0.2-017 — Propagación al perfil documental.**

La clasificación geométrica participa en la determinación del perfil documental. El defecto local puede influir en decisiones posteriores, aunque no se ha demostrado una clasificación incorrecta en un corpus.

**E-0.2-020 — Delimitación de la causa.**

Una clasificación anterior del extractor sí dispone del ancho físico real. El déficit documentado se localiza en la proyección posterior desde la representación estructural hacia el perfilado; no corresponde atribuirlo indiscriminadamente a toda la ingesta.

**E-0.6-010/028 — Propagación hacia G5.**

`RenderGeometryAdapter` utiliza dimensiones constantes de `612 × 792` puntos para producir geometría relativa. En el caso de figuras, esa información puede intervenir en la selección de representación para una o dos columnas.

La auditoría documenta la propagación de la misma causa de `GAP-0.2-02`, **no un GAP adicional**.

**Normalización trans-página — evidencia directa complementaria.**

La implementación examinada de `MetadataMerger.merge` concatena colecciones de BBox y conserva una lista deduplicada y ordenada de páginas.

Ese comportamiento acredita que el sistema admite procedencia multipágina. Sin embargo, la mera coexistencia de una lista de páginas y otra de geometrías no demuestra, por sí sola, una correspondencia inequívoca entre cada región utilizada y su página física.

No se afirma que toda asociación esté perdida ni se registra un nuevo GAP: esta observación justifica que el futuro contrato no presuponga una correspondencia inexistente.

**Normas históricas contrastadas.**

- `NADR-F17BIS-01` FROZEN establece representación canónica e integridad de serialización del AST.
- `NADR-F17BIS-02` FROZEN establece pureza hexagonal y política de proveedores de extracción.
- `NADR-F17BIS-04` contiene obligaciones de validación de Layout antes del AST, pero no cierra la garantía posterior AST→consumidores y su metadata mantiene pendiente la formalización editorial FROZEN.
- `NADR-FPPPR-02` FROZEN gobierna fidelidad de representación de contenido protegido y jerarquía en G5, no la producción y atribución de coordenadas físicas.

Estas normas aportan garantías compatibles, pero no expresan conjuntamente el contrato de procedencia geométrica verificable aquí propuesto.

## 5. REGLAS NORMATIVAS (RFC 2119)

**Las siguientes diez reglas RFC 2119 constituyen el contrato normativo FROZEN aprobado integralmente por el Architecture Board. Su implementación no queda autorizada por esta aprobación documental.**

### 5.1 Procedencia física y correspondencia entre páginas y regiones

1. Toda región o medida física utilizada para una decisión documental **MUST** conservar una atribución verificable al documento y a la página o páginas de origen pertinentes. Un identificador de página supuesto, de respaldo o no derivado de la procedencia acreditada **MUST NOT** presentarse como identidad física verificada.

2. Cuando un elemento lógico represente contenido procedente de varias páginas físicas, su procedencia **MUST** conservar las páginas acreditadas necesarias para interpretar las regiones utilizadas. Esa procedencia **MUST NOT** colapsarse silenciosamente en una página única ni tratarse como anomalía por el solo hecho de abarcar varias páginas.

3. Cuando una decisión documental utilice una región de un elemento con procedencia multipágina, **MUST** contar con una correspondencia verificable entre esa región y su página o páginas físicas de referencia, o **MUST** tratar la atribución como indeterminada. La coexistencia de colecciones separadas de páginas y geometrías, o la coincidencia de sus posiciones en una secuencia, **MUST NOT** tomarse por sí sola como evidencia suficiente de correspondencia individual.

### 5.2 Interpretación y transformación de geometría

4. Toda transformación de geometría utilizada para decisiones documentales **MUST** distinguir los sistemas de coordenadas y unidades relevantes, incluida la condición absoluta o normalizada de la entrada y las dimensiones físicas de referencia necesarias para interpretar el resultado. Los valores de sistemas distintos **MUST NOT** combinarse o sustituirse como equivalentes sin una transformación válida y verificable.

5. Toda coordenada o dimensión relativa **MUST** derivarse de una referencia física acreditada correspondiente a la página y región pertinentes, o de una transformación equivalente cuya validez esté demostrada. Un tamaño de página fijo, un valor por defecto o una estimación no corroborada **MUST NOT** utilizarse como si fuera la dimensión real verificada de una página diferente.

6. Cuando una decisión documental utilice una geometría representativa o agregada derivada de varias regiones o páginas, **MUST** mantener verificables su procedencia, su ámbito de cobertura y las propiedades físicas que esa derivación permite afirmar. Una proyección parcial o una combinación de referencias físicas incompatibles **MUST NOT** presentarse como geometría íntegra o válida para decisiones que requieran esa integridad, salvo que la suficiencia de la derivación esté demostrada para la decisión concreta.

### 5.3 Muestreo condicionado por páginas físicas

7. Toda política que declare un muestreo acotado por primeras páginas físicas **MUST** determinar su alcance mediante identidades y orden de páginas acreditados, conforme al contrato de muestreo aplicable. Identificadores ficticios, valores de respaldo o agrupaciones no demostradas **MUST NOT** utilizarse para acreditar el cumplimiento del límite declarado.

8. Cuando un elemento lógico abarque páginas incluidas y excluidas por un límite de muestreo, la política aplicable **MUST** definir y permitir verificar el tratamiento de sus regiones y la cobertura resultante. Una muestra que incorpore contenido de páginas excluidas **MUST NOT** ser aceptada como conforme a una política de acotación estricta, aunque esa sobrecobertura sea informada. Cuando no sea posible satisfacer el límite sin perder la integridad de un elemento, el resultado **MUST** conservar una condición explícita de incumplimiento o limitación respecto de la política aplicable y **MUST NOT** presentarse como cumplimiento íntegro. Una muestra que descarte contenido de páginas incluidas **MUST NOT** declarar cobertura completa de dichas páginas.

### 5.4 Insuficiencia de datos y trazabilidad de las decisiones

9. Cuando una decisión geométrica dependa de una página, correspondencia regional, dimensión o sistema de coordenadas no acreditado, el consumidor **MUST** identificar la limitación de forma atribuible y **MUST NOT** utilizar la propiedad incierta como si estuviera verificada. La consecuencia **MUST** respetar las obligaciones aplicables del consumidor y los contratos superiores, sin convertir automáticamente toda ausencia de geometría en un rechazo global del documento.

10. Toda decisión documental que dependa de información física derivada **MUST** permitir comprobar la procedencia y las transformaciones relevantes que sustentan esa decisión. La verificación de dicho linaje **MUST NOT** confundirse con identidad semántica del AST, identidad de generación traducida, identidad operacional ni certificación científica del PDF final.

## 6. CONSECUENCIAS ARQUITECTÓNICAS

- La procedencia de página deja de depender de atributos supuestos o valores de respaldo silenciosos.
- Los nodos multipágina permanecen compatibles con el alcance del proyecto y conservan las relaciones físicas necesarias para sus consumidores.
- Las transformaciones geométricas distinguen referencia absoluta, referencia relativa y dimensiones pertinentes.
- Las decisiones basadas en geometría pueden atribuirse a datos físicos efectivamente acreditados.
- Las políticas de muestreo pueden demostrar qué páginas y qué contenido quedan incluidos en su alcance.
- La incertidumbre de geometría no se convierte en una falsa certeza ni obliga, por sí sola, a descartar operaciones que no dependan de ella.
- Los consumidores de perfilado y reconstrucción quedan sujetos a garantías compatibles de procedencia, sin imponer un modelo físico único ni reproducir exactamente el diseño visual del PDF original.
- La trazabilidad física conserva su finalidad y no altera los contratos de identidad científica o ejecución.

## 7. VERIFICACIÓN Y VALIDACIÓN

**Estado: NOT_RUN.** Ninguna de las verificaciones o validaciones propuestas a continuación ha sido ejecutada en esta etapa documental.

### Verification — estática/mecánica

- Comprobar que las regiones físicas utilizadas por consumidores mantienen atribución verificable a su documento y página de origen.
- Comprobar que el contrato permite nodos con procedencia multipágina.
- Comprobar que la correspondencia entre regiones y páginas no se presupone por la simple presencia de dos colecciones.
- Comprobar que las transformaciones geométricas distinguen sistemas de coordenadas, unidades y referencias dimensionales.
- Comprobar que los consumidores de geometría derivada no tratan dimensiones de respaldo como medidas reales acreditadas.
- Comprobar que el muestreo utiliza identidades físicas válidas y tiene un tratamiento definido para nodos que cruzan el límite de páginas.
- Comprobar que una geometría incierta queda identificable sin contaminar los contratos de identidad semántica o científica.

### Validation — dinámica/comportamental

| **Falsador propuesto**                                                          | **Resultado exigido**                                                                                                                              |
| ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Elemento de la página 2 cuyo consumidor recibe un identificador de respaldo `0` | El respaldo no se presenta como página real acreditada ni permite validar falsamente un muestreo.                                                  |
| Nodo con regiones en páginas 2 y 3                                              | Ambas procedencias permanecen reconocibles; no se presume página única.                                                                            |
| Dos BBox y dos páginas sin vínculo individual acreditado, aun cuando sus colecciones tengan igual cardinalidad | La ambigüedad se declara; la coincidencia de posiciones en listas no acredita por sí sola una relación física. |
| Página física de 300 pt, elemento centrado en X = 210 pt                        | Posición relativa correcta de `0.70`, cuando ambas magnitudes pertenecen a esa página.                                                             |
| Página física de 400 pt, figura de ancho 300 pt                                 | Ancho relativo de `0.75`; un denominador no acreditado de 612 pt no puede presentarse como medida real.                                            |
| Documento con páginas de distintos tamaños                                      | Cada geometría derivada utiliza la referencia correspondiente, sin propagar indiscriminadamente una dimensión común.                               |
| Entrada con coordenadas ya normalizadas                                         | No se vuelve a dividir como si fueran coordenadas absolutas.                                                                                       |
| Política de primeras N páginas con nodos provenientes de páginas posteriores    | La muestra respeta el alcance declarado; no considera equivalentes páginas distintas por compartir un valor ficticio.                              |
| Nodo multipágina que cruza las primeras N páginas y cuya muestra incorpora contenido posterior | El resultado no supera ni se acepta como conforme al contrato de muestreo estrictamente acotado, aun cuando informe la sobrecobertura. |
| El consumidor descarta íntegramente un nodo multipágina para respetar el límite | Puede conservar la acotación estricta, pero no afirma cobertura completa de las páginas incluidas si descartó contenido de ellas. |
| La política admite explícitamente una muestra parcial | El alcance y la limitación reales son verificables; la parcialidad no se presenta como cumplimiento de una garantía de cobertura superior. |
| Nodo con geometría ausente pero contenido lógico válido                         | No se fabrica una decisión geométrica; otras capacidades pueden continuar solo cuando sus contratos lo permitan.                                   |
| Geometría representativa tomada de una región de un nodo multipágina | Se acredita el alcance y la suficiencia para la decisión concreta; la región parcial no se hace pasar por geometría íntegra de todo el nodo. |
| Decisión de perfilado o render vinculada a un dato físico erróneo               | La procedencia y transformación utilizada permiten atribuir el origen de la discrepancia, sin afirmar automáticamente un fallo científico del PDF. |

Los falsadores de contrato pueden diseñarse con documentos y geometrías sintéticas. Su ejecución corresponde al futuro Execution Plan aprobado.

La evaluación de fidelidad física o científica con PDFs reales requiere criterios, corpus y autorizaciones independientes bajo la gobernanza PPPR.

## 8. RELACIÓN CON OTROS ARTEFACTOS

| **Artefacto**                                                | **Relación**                                                                                                                                           |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `ADR_PPPR_MASTER.md` FROZEN                                  | **Autoridad constitucional:** preservación STEM y linaje documental (§5); necesidad de examinar obligaciones normativas residuales (§8.1).             |
| `HITO_PPPR.0.2` FROZEN                                       | **Evidencia principal:** `GAP-0.2-01/02`, `E-0.2-011/012/013/017/020`.                                                                                 |
| `HITO_PPPR.0.6` FROZEN                                       | **Evidencia de propagación:** `E-0.6-010/028`; no crea un GAP nuevo para la misma causa.                                                               |
| `HITO_PPPR.0.9` FROZEN                                       | **Reconciliación causal:** mantiene separados los GAP de muestreo y geometría y no multiplica la propagación hacia G5.                                 |
| `PROJECT_SCOPE.md`                                           | **Fundamento de producto:** normalización trans-página, AST secuencial, perfil y reconstrucción de layout.                                             |
| `ENGINEERING_PRINCIPLES.md`                                  | **Principios superiores:** explicitud, datos inmutables, cero fallos silenciosos y trazabilidad de índices físicos.                                    |
| `NADR-F17BIS-01` FROZEN                                      | **Ámbito compatible:** representación, validación y serialización canónica del AST; no define por sí mismo la semántica geométrica de cada consumidor. |
| `NADR-F17BIS-02` FROZEN                                      | **Ámbito compatible:** puertos y política de extracción, no correspondencia de geometría entre páginas y consumidores.                                 |
| `NADR-F17BIS-04` APPROVED, formalización editorial pendiente | **Contraste de frontera:** validación física previa al AST; no se le atribuye cierre FROZEN de la procedencia posterior.                               |
| `NADR-F17BIS-03/16` FROZEN                                   | **Separación de capacidades:** identidad semántica y contratos de hash por propósito.                                                                  |
| `NADR-FPPPR-02` FROZEN                                       | **Capacidad complementaria:** representa contenido y jerarquía válidos en G5; no determina la procedencia geométrica upstream.                         |
| `NADR-FPPPR-01` FROZEN                                       | **Autoridad científica:** gobierna legitimidad, evidencia y vigencia de las afirmaciones de conformidad del PDF final.                                 |
| Futuro `PHASE_PPPR_EXECUTION_PLAN.md`                        | **Destino de materialización:** decisiones de implementación, trazabilidad a reglas, falsadores y secuencia de cambios tras aprobación.                |

Las relaciones con NADR existentes son de **compatibilidad y delimitación**, no dependencias normativas directas nuevas. No se declaran relaciones recíprocas que los contratos históricos no contengan.

El Architecture Board aprobó la clasificación de relaciones de §8 tras revisión integral conforme a `4_METH_NADR.md`. No se modifican documentos FROZEN de otras capacidades para fabricar reciprocidad.

## 9. FRONTERA NORMATIVA (QUÉ NO GOBIERNA ESTE NADR)

- **No gobierna** selección de motores OCR, política de proveedores, pureza hexagonal ni capacidades generales de extracción; los contratos `NADR-F17BIS-02` solo son relevantes para la ruta única en el ámbito cuya compatibilidad haya sido acreditada.
- **No gobierna** serialización canónica del AST ni prescribe modificar su formato físico; `NADR-F17BIS-01` mantiene su autoridad.
- **No prescribe** un campo `page_width` por nodo, listas paralelas, pares de datos, tablas de dimensiones ni una arquitectura física determinada para mantener correspondencia de página y región.
- **No impone** que cada nodo lógico tenga una sola página o un solo BBox; la normalización trans-página sigue siendo parte del alcance aprobado.
- **No gobierna** algoritmos específicos de clasificación de columnas, umbrales geométricos, estilos, tamaños de página fijos o técnicas concretas de ensamblado.
- **No garantiza** reconocimiento OCR universal de texto rasterizado, extracción semántica de tablas, recuperación de fórmulas o interpretación completa de gráficos vectoriales.
- **No impone** reconstrucción visual pixel-perfect ni aceptación automática de la equivalencia geométrica entre PDF fuente y PDF reconstruido.
- **No gobierna** la traducción EN→ES, admisión de proveedores LLM, presupuestos o egress; se mantienen los contratos PPPR aplicables.
- **No gobierna** identidad semántica del AST, identidad de generación traducida, identidad de intento operacional ni fórmulas criptográficas; se conservan DC-04 y los NADR FROZEN pertinentes.
- **No gobierna** certificación científica integral del PDF final, que corresponde al ADR Maestro y `NADR-FPPPR-01`.
- **No introduce** estados operacionales, mecanismos de recuperación o reintentos que alteren los contratos F18.
- **No prescribe** tareas, responsables individuales, algoritmos, bibliotecas, Definition of Done, ejecución de pruebas o despliegues; esas decisiones pertenecen al futuro Execution Plan y sus autorizaciones.

**Nota de gobernanza:** las diez reglas constituyen el contrato normativo FROZEN de esta capacidad. La aprobación y el merge interno no reparan los GAP de PPPR.0.2, no ejecutan falsadores (`NOT_RUN`), no acreditan fidelidad científica ni autorizan código, pruebas físicas, egress, gasto o integración a `main`. La implementación requiere el Execution Plan aprobado y sus autorizaciones independientes.