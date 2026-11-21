# NADR-FPPPR-01: Legitimidad y Trazabilidad de la Conformidad Científica del PDF Final EN→ES

**FROZEN v1.0.0 — aprobación integral del Architecture Board comunicada por el owner el 2026-11-20.**

## 1. METADATA

* **Decision ID:** NADR-FPPPR-01
* **Título:** Legitimidad y Trazabilidad de la Conformidad Científica del PDF Final EN→ES.
* **Clase de Decisión:** GOVERNANCE / DATA.
* **Nivel de Cumplimiento:** MANDATORY.
* **Versión:** 1.0.0.
* **Ciclo de Vida:** FROZEN.
* **Fecha de Aprobación Integral:** 2026-11-20, comunicada expresamente por el owner como decisión del Architecture Board respecto del contenido del PR #76, HEAD `575b1a5838e043e383257eaba8f7613a04190190` (borrador v0.4.0).
* **Fecha de Congelamiento:** 2026-11-20; FROZEN autorizado en la misma comunicación.
* **Procedencia de Autoridad:** Comunicación directa del owner en esta conversación; no se presume acta externa, firma ni revisión GitHub formal independiente.
* **Vigente Desde:** Etapa normativa PPPR — 2026-11-20, tras aprobación integral del Board. Vincula el futuro Execution Plan PPPR conforme a la metodología; no autoriza por sí mismo implementación ni certificación de producto.
* **Autoridad:** Architecture Board.
* **Responsable Técnico:** Staff Engineering / PPPR — rol ratificado por aprobación integral del NADR; no se designa una persona.
* **Capacidad Arquitectónica:** `CAP-PPPR-01` (Legitimidad, atribuibilidad y vigencia de conformidad científica PDF final EN→ES) — Gobernar la correspondencia verificable entre sujeto, evidencia independiente, criterios autorizados, resultados y validez temporal del dictamen científico del PDF final traducido. Código ratificado en la aprobación integral de este NADR.
* **Evidencia Forense:** E-0.8-006/014/020/021; E-0.9-016…019; E-0.6-024; DQ-0.8-01…05. Los E-IDs citados son P2 históricos; no se crean GAP nuevos.
* **Referencias Cruzadas:**
  * **Depende de:** ADR_PPPR_MASTER.md FROZEN (DC-09/10/11/12) como autoridad constitucional superior.
  * **Influencia prevista:** futuro Execution Plan único PPPR, sujeto a aprobación; no constituye todavía dependencia normativa recíproca de otro NADR.
  * **Contraste sin adopción:** NADR-F17BIS-23/24/25/27/28 FROZEN, dentro de sus sujetos históricos.
  * **Conflictúa con:** declarar conformidad científica desde extraction-only, proveedor fake, compilación, evidencias incompletas o referencias sin autoridad.
  * **Reemplaza a:** N/A.

**Excepción documental autorizada:** el namespace NADR-FPPPR-{XX} y la ubicación en docs/architecture/adr/pdf-pdf-product-readiness/NADR/ se aplican únicamente a la iniciativa transversal PPPR. No crean una fase numerada del ROADMAP ni modifican la metodología FROZEN.

## 2. ARCHITECTURE RISK SCORE

Puntuación de riesgo arquitectónico ratificada en la aprobación integral del NADR. No representa incidentes medidos ni modifica la clasificación de GAP históricos.

| Dimensión | Puntaje | Justificación |
| :--- | ---: | :--- |
| Operacional | 4/5 | Posible atribución de conformidad científica a una salida técnicamente válida pero no evaluada. |
| Mantenibilidad | 3/5 | Ambigüedad entre sujeto, referencia, criterios y resultado atribuible. |
| Recuperabilidad | 3/5 | Dificultad para reconstruir el fundamento o determinar vigencia de un dictamen anterior. |
| Seguridad | 2/5 | Riesgo de referencias utilizadas sin procedencia o autoridad acreditadas; no existe incidente acreditado. |
| Financiero | 3/5 | Decisiones o evaluaciones costosas sustentadas en afirmaciones científicas inválidas. |
| **Total** | **15/25** | **S2 — ALTO, ratificado por el Board.** |

* **Total Score:** `15/25` — suma de las cinco dimensiones.

**Severidad:** `S2` (ALTO), ratificada en aprobación integral del Board.

## 3. DECISIÓN EJECUTIVA

**Toda afirmación de conformidad científica del producto PPPR deberá referirse al PDF final EN→ES efectivamente generado y estar sustentada en evidencia atribuible, independiente y suficiente, evaluada mediante referencias y criterios científicamente autorizados antes de la evaluación certificante.**

En consecuencia:

* La conformidad científica no se infiere de extracción, compilación ni publicación del PDF.
* Solo se declaran las dimensiones de calidad que estén suficientemente acreditadas.
* La autoridad de referencias y criterios no nace de la configuración ni de la ejecución de una herramienta.
* La vigencia de una afirmación depende del sujeto y de los fundamentos bajo los que fue emitida.

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La ruta productiva PPPR seleccionada es CLI → OCR → G3 → G5 → PDF, con objetivo de entregar un PDF científico traducido EN→ES. La Continuous Verification histórica evalúa extracción PDF→AST frente a referencias topológicas; no acredita por sí sola fidelidad lingüística, integridad STEM o fidelidad estructural/visual del producto final.

Se identifican cuatro riesgos normativos:

1. **Sustitución de sujeto:** una prueba de extracción, fake o compilación se utiliza como supuesto testigo de calidad del PDF traducido.
2. **Referencia no acreditada:** se usa un oráculo o criterio sin procedencia, independencia o autoridad científica verificable.
3. **Atribución incorrecta:** el resultado se relaciona con otra generación, versión de criterios o PDF distinto del evaluado.
4. **Conformidad positiva inválida:** evidencia ausente, resultados parciales o fallos operacionales se interpretan como certificación.

### 4.2 Manifestación concreta identificada por la auditoría

* **E-0.8-006 / E-0.9-016 (P2):** tools/evaluation/run_regression.py::run_evaluation usa un pipeline de extracción y compara AST con oráculos AST; no verifica científicamente G3→G5 ni el PDF final EN→ES.
* **E-0.8-014 (P2):** la evidencia CI de estabilización pertenece a un commit y sujeto históricos, no a aceptación bilingüe actual.
* **E-0.8-020/021 (P2):** la convergencia OCR→G3→G5 con proveedor fake y la publicación física de PDF son testigos operacionales, no certificación lingüística, STEM ni visual.
* **E-0.6-024 (P2):** una cabecera PDF válida y FSM COMPLETED no equivalen a conformidad científica; la salida distingue NOT_CERTIFIED.
* **E-0.9-017 (P2):** 21 documentos/GT históricos y 15 PDF originales no materializados en Git; su acceso, licencia, custodia y uso siguen condicionados al owner y al issue #34.
* **DQ-0.8-02/03/04:** faltan referencias bilingües autorizadas, evidencia de independencia experimental y validación real de las dimensiones científicas del PDF español.

Estas observaciones no crean GAP P1 nuevos ni demuestran que se haya emitido una certificación falsa en producción.

## 5. REGLAS NORMATIVAS (RFC 2119)

**Reglas normativas vigentes para esta capacidad tras la aprobación integral y FROZEN de este NADR.**

### 5.1 Sujeto y dimensiones de conformidad PPPR

1. Toda afirmación de conformidad científica de PPPR **MUST** identificar inequívocamente el PDF final EN→ES efectivamente evaluado y la generación a la que pertenece.

2. Toda afirmación de conformidad científica integral **MUST** estar sustentada en evidencia suficiente para las tres dimensiones del ADR Maestro: fidelidad lingüística, integridad STEM y fidelidad estructural/visual, conforme a criterios autorizados. Una evaluación parcial **MUST NOT** presentarse como conformidad integral.

3. La conformidad científica del PDF final **MUST NOT** fundamentarse exclusivamente en extracción PDF→AST, pruebas con proveedor fake, compilación exitosa, validez binaria del PDF o estados operacionales terminales. Estos resultados **MAY** servir como evidencia técnica complementaria cuando sus límites estén identificados.

### 5.2 Admisibilidad y autoridad de la evidencia

4. Toda referencia utilizada para sustentar una afirmación positiva **MUST** tener identidad, procedencia, elegibilidad y condiciones de utilización verificables conforme a una política de autoridad previamente aprobada y aplicable a PPPR. La existencia de una referencia, su integridad criptográfica o su aceptación técnica **MUST NOT** interpretarse por sí sola como autoridad científica.

5. La evidencia presentada como independiente **MUST** cumplir las condiciones de independencia del modelo de confianza aprobado. La salida evaluada **MUST NOT** constituir su única prueba independiente de corrección. Esta obligación no prohíbe que un evaluador autorizado examine el PDF final: prohíbe la autovalidación sin fundamento independiente suficiente.

6. Los criterios que determinan si la calidad científica es suficiente para emitir conformidad positiva **MUST** estar definidos, versionados y aprobados por la autoridad competente **antes de comenzar la evaluación destinada a sustentar esa conformidad**. La selección retrospectiva de criterios a partir de los resultados, la mera configuración técnica o la decisión unilateral de un Execution Plan **MUST NOT** establecer dicha suficiencia.

**Límite de autoridad:** las reglas 4–6 consumen políticas y criterios aprobados; no crean un modelo de confianza nuevo, no designan evaluadores ni establecen quién tiene autoridad para constituir oráculos o aprobar umbrales. Sin autoridad acreditada, no puede emitirse conformidad científica positiva. Las evaluaciones exploratorias no certificantes no adquieren legitimidad científica por este contrato.

### 5.3 Atribución y vigencia del dictamen

7. Toda afirmación científica positiva **MUST** mantener una relación verificable entre documento fuente, identidad y contrato de generación relevantes, PDF final evaluado, referencias utilizadas, versiones de criterios aplicados y resultado obtenido. La ausencia de un vínculo necesario **MUST** impedir atribuir conformidad positiva a esa generación.

8. Un dictamen científico **MUST** atribuirse únicamente al PDF final efectivamente evaluado. Si el artefacto al que se pretende atribuir difiere del sujeto evaluado, ese dictamen **MUST NOT** presentarse como conformidad del nuevo artefacto. La coincidencia de nombre, ruta o metadatos **MUST NOT** considerarse demostración de identidad científica ni autorizar el traslado del dictamen a otro PDF.

9. Cuando cambie una referencia o un criterio relevante para el fundamento de una afirmación, su vigencia **MUST** determinarse según las reglas de validez aprobadas antes de presentarla como conformidad actual. Si esa vigencia no puede acreditarse, la afirmación **MUST NOT** declararse vigente. La evidencia histórica **MUST** conservar la atribución y el contexto de la evaluación original; la pérdida de vigencia no autoriza reescribir el resultado anterior.

### 5.4 Certificación sin falsos positivos

10. Para cada dimensión y alcance objeto de una afirmación, una evaluación inválida, incompleta, carente de evidencia necesaria o interrumpida por un fallo operacional **MUST NOT** producir conformidad científica positiva respecto de ese alcance. La falta o invalidez de evidencia en una dimensión **MUST NOT** invalidar automáticamente el resultado científico válido de otra; tal resultado **MUST** conservarse identificado estrictamente con su dimensión y alcance y **MUST NOT** interpretarse como certificado parcial de producto, conformidad integral ni conformidad del PDF final. Las evaluaciones inválidas o incompletas **MUST** distinguirse de un rechazo científico válido y **MUST NOT** interpretarse automáticamente como demostración de divergencia científica.

11. Un PDF parcial, DEGRADED o expresamente no certificado **MUST NOT** presentarse como resultado final científicamente conforme de PPPR. Los artefactos de diagnóstico o recuperación **MAY** conservarse bajo una identificación inequívoca de su condición no conforme, dentro de los límites de DC-12.

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* La conformidad científica constituye una afirmación sustentada en evidencia y atribuida a un PDF final concreto, no al estado de su proceso.
* Las tres dimensiones de calidad permanecen distinguibles; ninguna prueba técnica aislada sustituye la evaluación integral.
* Las referencias y criterios científicos mantienen autoridad separada de las herramientas que los consumen.
* Evaluación científica desfavorable válida, ausencia de evidencia y fallo operacional no se confunden.
* La pérdida de vigencia no destruye ni reescribe evidencia histórica.
* Pueden reutilizarse mecanismos compatibles con el sujeto PPPR, pero no se importan automáticamente marcos ni taxonomías históricos.

## 7. VERIFICACIÓN Y VALIDACIÓN

Falsadores previstos para implementación y evaluación posteriores bajo gobernanza aprobada. **NOT_RUN** en esta etapa documental.

**Verification (estática / mecánica):**

* Verificar que una afirmación positiva identifique PDF final, generación, dimensiones, referencias, criterios aprobados y resultado.
* Verificar que la autoridad de referencias y criterios no se infiera de archivos, hashes o valores de configuración.
* Verificar la distinción entre evaluación científica válida, fallo operacional e incompletitud.
* Verificar que un dictamen permanezca atribuido al PDF final efectivamente evaluado y no pueda trasladarse a otro artefacto por coincidencia de nombre, ruta o metadatos.
* Verificar que los resultados científicos válidos por dimensión preserven su alcance sin convertirse en certificados parciales de producto, conformidad integral ni conformidad del PDF final.

**Validation (dinámica / comportamental):**

| Falsador propuesto | Resultado exigido |
| :--- | :--- |
| PDF técnicamente válido, sin evidencia científica suficiente | Sin conformidad positiva. |
| Solo extracción PDF→AST o proveedor fake | No certifica la traducción final. |
| Falta evidencia de una dimensión exigida | No emitir conformidad integral. |
| Referencia sin autoridad acreditada | No emitir conformidad positiva. |
| La propia salida evaluada se presenta como única prueba independiente de su corrección | Rechazar la evidencia como independencia suficiente; no emitir conformidad positiva basada en autovalidación. |
| Criterio seleccionado después de observar resultados | No certificar con ese criterio retrospectivo. |
| Dictamen de otro PDF final, aunque nombre, ruta o metadatos coincidan | No atribuirlo al nuevo sujeto; no se autoriza transferencia de conformidad entre PDFs. |
| Cambio de referencia o criterio relevante sin vigencia acreditada | No reutilizar dictamen como vigente; conservar sin reescribir la evidencia histórica atribuida al resultado original. |
| Evaluación lingüística válida, dimensión visual sin evidencia suficiente | Conservar el resultado lingüístico con alcance explícito como evidencia científica; no emitir certificado parcial de producto, conformidad integral ni declarar conforme el PDF final. |
| Evaluación válida con resultado desfavorable | Rechazo científico distinguible de fallo operacional. |
| Evaluación incompleta o fallida | No emitir conformidad positiva ni inventar divergencia. |
| Artefacto parcial o DEGRADED | No presentarlo como conforme. |

Los falsadores abstractos de atribución pueden diseñarse sin corpus privado. La validación científica real requiere referencias legítimas, criterios aprobados, permisos y Execution Plan autorizado.

## 8. RELACIÓN CON OTROS ARTEFACTOS

**Interpretación de relaciones:** los contratos F17-BIS y F18 conservan autoridad normativa dentro de sus ámbitos vigentes. Su aplicabilidad a cada obligación PPPR depende del sujeto, la responsabilidad, las condiciones y la compatibilidad demostrada; no se presume por analogía ni se excluye globalmente. F17-BIS aporta contrastes históricos de certificación PDF→AST, mientras F18 mantiene autoridad aplicable a responsabilidades operacionales de la ruta PPPR (ejecución, efectos inciertos y recuperación) donde sus contratos así lo gobiernan. Este NADR no modifica esas fronteras.

| Artefacto | Relación |
| :--- | :--- |
| ADR_PPPR_MASTER.md FROZEN | **Autoridad superior:** DC-09 fija sujeto y dimensiones; DC-10 condiciona custodia; DC-11 delimita tooling histórico; DC-12 excluye DEGRADED conforme. |
| HITO_PPPR.0.8 FROZEN | **Evidencia forense:** CV PDF→AST y límites de los testigos operacionales. |
| HITO_PPPR.0.9 FROZEN | **Reconciliación:** E-0.9-016…019; evidencia de diferencia de sujeto. |
| NADR-F17BIS-23 FROZEN | **Contraste histórico:** calibración e independencia específicas, sin adopción del protocolo completo. |
| NADR-F17BIS-24 FROZEN | **Contraste histórico:** integridad de certificación y separación de resultados de su ámbito. |
| NADR-F17BIS-25 FROZEN | **Delimitación de sujeto:** CV extracción PDF→AST no certifica el PDF final EN→ES. |
| NADR-F17BIS-27/28 FROZEN | **Contraste histórico:** semántica de resultados y trazabilidad de CV, sin importar estados ni baseline. |
| NADR-F18-03/04/05 FROZEN | **Responsabilidad operacional aplicable por ámbito:** autoridad de ejecución y efectos inciertos, persistencia recuperable y observabilidad de intentos. Conservan fuerza dentro de su alcance en la ruta PPPR; no constituyen reglas sobre el oráculo ni el dictamen científico de este NADR. |
| Política científica futura, si fuese necesaria | **Condición de autoridad:** solo una decisión arquitectónica competente puede establecer un nuevo modelo de confianza o autoridad científica que exceda el Maestro. |
| Futuro Execution Plan PPPR único | **Destino de implementación:** no crea por sí mismo normas, políticas científicas ni permisos. |

**Reciprocidad y precedencia:** este documento no declara dependencia normativa directa de los NADR históricos. No los modifica ni presupone reciprocidad con documentos FROZEN. Las dependencias nuevas que se prueben necesarias deberán seguir el procedimiento de autoridad y reciprocidad de 4_METH_NADR.md §8. La subordinación constitucional al Maestro ya está prevista en el ADR PPPR §8.1.

## 9. FRONTERA NORMATIVA (QUÉ NO GOBIERNA ESTE NADR)

* **No gobierna** la Continuous Verification histórica de extracción PDF→AST, sus Ground Truth sellados, su baseline o su evaluación topológica.
* **No adopta automáticamente** reglas ajenas a su sujeto por su estado FROZEN. Las obligaciones F17-BIS/F18 conservan autoridad dentro de sus ámbitos; F18-03/04/05 continúan gobernando las responsabilidades operacionales aplicables de la ruta PPPR sin que este NADR las reinterprete o sustituya.
* **No decide** quién constituye, valida o aprueba oráculos científicos EN→ES ni crea un modelo de confianza de evaluadores.
* **No determina** métricas, umbrales, algoritmos, protocolos estadísticos, particiones o tamaños de muestra.
* **No permite** que una ejecución, configuración técnica o Execution Plan cree autoridad científica retrospectivamente.
* **No autoriza** el acceso a corpus privados, la obtención de los quince PDF ausentes, la transmisión a terceros ni contratación de proveedores.
* **No gobierna** inferencia G3, renderizado G5 ni fórmulas criptográficas de identidad de generación; tampoco gobierna autoridad de ejecución, efectos inciertos o recuperación operacional, bajo los contratos F18 aplicables.
* **No prescribe** clases, módulos, formatos, herramientas, tecnologías, tareas, Definition of Done o despliegues; esas responsabilidades pertenecen al Execution Plan aprobado.

**Nota de gobernanza:** las once reglas RFC 2119 constituyen el contrato normativo FROZEN de esta capacidad. Su aprobación no equivale a certificación científica PPPR, no constituye ni autoriza oráculos o criterios de calidad no aprobados, no altera el ADR Maestro FROZEN y no habilita evaluación física, comercial o con corpus privado sin permisos y planificación correspondientes.
