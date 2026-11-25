# ARCHITECTURE DECISION RECORD (ADR)
## ADR PPPR 02 (candidato sucesor focal): Aceptación productiva de alcance personal

* **Estado:** APPROVED — alcance sucesor focal ratificado expresamente por el owner en calidad de autoridad arquitectónica del proyecto (2026-11-25); sin aprobación científica.
* **Acto y objeto de aprobación:** Ratificación arquitectónica expresa del owner, 2026-11-25, ante solicitud específica de aprobar ADR PPPR 02 v0.1.0 en calidad de autoridad arquitectónica del proyecto: «Si, estoy de acuerdo. adelante con eso». Objeto ratificado: commit `070d8e43a272222756671f154b5c203192793be3`, blob `b2ce91e9878e8c2e807831817e32c6f9dd61a572`. Se registra el acto comunicado directamente en conversación; no se atribuye revisión formal GitHub, firma externa ni dictamen independiente de otro Board. Staff favorable; el owner ejerce la autoridad arquitectónica para esta decisión focal. No constituye aprobación científica ni autorización de datos, proveedor, coste, host, activación o merge.
* **Versión:** 0.1.0.
* **Fecha de Emisión:** 2026-11-25.
* **Autor:** Staff Engineering / PPPR.
* **Fase Parent:** PDF→PDF Product Readiness (PPPR, sin fase nueva de ROADMAP).
* **Baseline de decisión:** `6acac34021dc11589322f383b10ffdadc50b91f4` (PR #95 Draft).
* **Evidencia Forense Vinculante:** GF-02, Evidence Log §2.2; HITO PPPR.0.8 E-0.8-006/020/021/026/046/047, PPPR.0.9 E-0.9-016…019, issue #34 comentario 7168477544.
* **Referencias Cruzadas:**
  * **Depende de:** [ADR Maestro FROZEN](ADR_PPPR_MASTER.md), [ADR PPPR 01](ADR_PPPR_01_Autoridad_y_Confianza_Cientifica.md) en alcance arquitectónicamente aceptado.
  * **Implementado por:** [NADR-FPPPR-01](../NADR/NADR_01_Conformidad_Cientifica_PDF_EN_ES.md) R1–R11 para afirmaciones científicas; restantes NADR PPPR y obligaciones históricas aplicables, sin promulgación nueva.
  * **Ejecutado por:** [Execution Plan único](../plans/PHASE_PPPR_EXECUTION_PLAN.md), §2.6, únicamente después de decisión competente y reconciliación.
  * **Supersede efectivo, alcance focal ratificado:** exclusivamente la obligatoriedad de culminar el alcance personal inicial mediante aceptación científica positiva de DC-09/§5.8/§10 Nivel B del Maestro, en cuanto implica el cierre certificante como único cierre de PPPR. Preserva sujeto, independencia, tres dimensiones y demás garantías del Maestro.
  * **Conflictúa con:** interpretar el cierre positivo certificante actual del plan como satisfecho por un ensayo funcional.

> Nota de gobernanza: ADR de Fase con alcance sucesor explícito conforme a 2_METH_ADR_MASTER.md §6 y metodología general §§2,3.1–3.4; estructura de 3_METH_ADR_SUBPHASES.md. No se editan bytes FROZEN. La ratificación expresa indicada en el header es distinta del acuerdo preliminar sobre la propuesta; se conserva la revisión candidata exacta en Git.

## 1. CONTEXTO Y JUSTIFICACIÓN

GF-02 identifica una diferencia real de alcance: el owner quiere un traductor científico EN→ES de calidad productiva para uso personal, mientras que el criterio actual de salida de PPPR exige conformidad científica positiva bajo autoridad acreditada. Los HITO PPPR.0.8/0.9 distinguen correctamente extracción, prueba fake y PDF final; esa separación permanece.

La baseline v3.9 tiene 21 PDF cuya identidad física fue comprobada localmente por el owner (21/21, cero faltantes o discrepancias); sus 21 GT son de extracción, no oráculos bilingües. Los tres pares candidatos complementarios ya disponibles tienen límites documentados. CI técnica del checkpoint GF-02 SUCCESS, pero no existe acto de aprobación científica ni candidato evaluado. La diferencia no se resuelve repitiendo adquisiciones ni haciendo pasar CI por ciencia.

## 2. PROBLEMA ARQUITECTÓNICO

La admisibilidad del producto para un ámbito personal y la legitimidad de una afirmación científica integral tienen objetos de decisión distintos. Mezclarlos bloquea la aceptación funcional por una autoridad externa al propósito de uso o fomenta un PASS sin fundamento. El problema no es un defecto probado del control fail-closed, ni una razón para reducir calidad. Son dimensiones independientes: calidad observada del PDF, suficiencia para uso personal autorizado y legitimidad de una afirmación certificante.

Alternativas examinadas: mantener el cierre certificante y esperar autoridad científica acreditada (válida, pero no responde por sí sola al objetivo personal); declarar equivalencia entre validación funcional y ciencia (rechazada); separar explícitamente la aceptación personal del dictamen científico, conservando sus exigencias técnicas y trazabilidad (propuesta). La ausencia de una autoridad científica no prueba que el producto funcione ni que falle.

## 3. DECISIÓN ARQUITECTÓNICA

**Decisión ratificada:** la aceptación productiva de alcance personal puede constituir un cierre operativo autónomo de PPPR exclusivamente sobre evidencia suficiente del PDF final real EN→ES y controles operacionales vigentes, sin emitir ni implicar conformidad científica positiva; esta última permanece sujeta íntegramente al modelo de autoridad e independencia de NADR-FPPPR-01 y ADR PPPR 01.

Consecuencias:
* Mismo producto, única ruta soportada, mismo sujeto físico e identidades; no un segundo pipeline.
* La aceptación personal se limita a documentos, capacidades, versiones y condiciones efectivamente probados; no garantiza generalización, equivalencia científica integral ni SOTA medido.
* Toda afirmación positiva científica queda en el camino certificante existente, fail-closed. No se modifica ninguna regla R1–R11, ningún oráculo sellado ni criterio científico aprobado.
* La decisión personal del owner no sustituye competencia necesaria para interpretar significado. Se exige contraste independiente de fuente, referencia y salida, criterios fijados previamente y evidencia atribuible. Incertidumbre material sin resolver impide aceptación del alcance afectado.
* Distinción documental del cierre: un eventual G6 completado bajo alcance personal no certificante no es G6 PASS científico. PRODUCT_READINESS=NOT_CERTIFIED conserva el significado vigente; no se redefine PASS ni se altera un enum runtime por nomenclatura. El estado de uso personal autorizado se registra separadamente, con alcance y límites. PRODUCT_DISPATCH conserva su propio gate de autorización; ningún permiso se infiere.

## 4. OBJETIVO DE LA SUBFASE

Obtener evidencia reproducible de un traductor utilizable por el owner con exigencia de fidelidad lingüística, matemática/técnica y estructural/visual en el alcance probado, sin atribuir legitimidad que la evidencia no sostiene.

> Menos formalización no significa menos control de calidad: el PDF final real y la evidencia independiente siguen siendo el fundamento de aceptación.

## 5. ALCANCE Y NO-OBJETIVOS

Dentro: distinción de aceptación personal y conformidad científica, delimitación de afirmaciones y estados, conservación de evidencia, permisos y seguridad, reutilización del benchmark histórico como evidencia técnica complementaria.

Fuera: certificación científica sin autoridad (ADR PPPR 01/NADR-FPPPR-01); ampliación de idiomas, UI, nueva plataforma de evaluación o segundo pipeline (Maestro/ROADMAP); cambios en baseline, GT o materialización privada en CI (owner/issue #34); elección/activación de proveedor y egress (permisos y Execution Plan); criterios concretos, inventario, falsadores y secuencia (protocolo aplicable y Execution Plan después de resolución). No se exige una institución certificadora ni se presume que toda revisión personal sea competente. No se abre una fase nueva.

## 6. GOBERNANZA DE LA SUBFASE

Preservar DC-04/05/06/08/10/11/12 y la parte sustantiva de DC-09: PDF final EN→ES, evidencia independiente de las tres dimensiones, linaje y límites. La única sucesión propuesta es el objetivo de cierre inicial personal frente a la obligatoriedad de cierre certificante. Las reglas de afirmación científica de NADR-FPPPR-01 permanecen intactas; los controles de admisión científicos existentes no se eluden ni reutilizan como vía de aprobación personal.

No se exige un nuevo NADR si el contraste posterior demuestra que las obligaciones existentes cubren el alcance sin contradicción. Si una nueva obligación normativa es necesaria, se resolverá conforme a metodología antes de implementar. El protocolo científico v0.3.0 conserva bytes, identidad y condiciones de aprobación. No se le atribuye vigencia científica por este ADR.

## 7. ARQUITECTURA OBJETIVO

```text
Única ruta PPPR real y autorizada → PDF final EN→ES atribuible
                    │
     evidencia independiente, permisos, integridad y trazabilidad
                    │
       ┌────────────┴─────────────┐
 aceptación personal        conformidad científica
 alcance probado            autoridad + R4–R6 + evaluación válida
 no certificante            camino existente, fail-closed
       └────────────┬─────────────┘
     resultados separados, sin inferencia automática de uno al otro
```

La aceptación personal exige resultados suficientes en cada dimensión aplicable, sin compensación; no acepta DEGRADED, fake, regresión de extracción sola, resultados incompletos o defectos materiales no resueltos. Ninguna evaluación se inicia sin permiso de materiales y efectos externos. La evidencia técnica histórica complementa, no sustituye la evidencia del PDF final.

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación | Estado de referencia |
|---|---|---|
| ADR Maestro DC-09/§5.8/§10 Nivel B | sucesión focal ratificada, resto intacto | FROZEN original; sin modificación |
| ADR PPPR 01 y NADR-FPPPR-01 | preserva camino certificante | identidades originales intactas |
| Protocolo v0.3.0 | conserva metodología y requisitos científicos | no aprobación científica atribuida |
| Plan / Register / Evidence Log | GF-02, secuencia y disposición futura | vínculo LIVING, sin cambio de criterio vigente |
| Issue #34 / HITO PPPR.0.8 | custodia y límites de evidencia histórica | OPEN, sin DF duplicado |

## 9. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

Metodología general §§2,3.1–3.4 y 2_METH_ADR_MASTER.md §6 permiten sucesor explícito y prohíben redefinir desde el plan. Este ADR define qué y por qué; no legisla implementación ni aprueba criterios retrospectivos. Se solicita **una decisión focal única del Board**: aceptar o rechazar la sucesión limitada, confirmar los límites de estados y la conservación de las reglas. Si se aprueba, regularizar GF-02 en el mismo PR, verificar compatibilidad normativa y reconciliar las cuatro Tasks restantes y sus criterios de salida sin reducir garantías ni iniciar efectos externos por inferencia. Si se rechaza, permanece el cierre certificante original y la alternativa personal requiere otra disposición competente. No se presume ratificación por acuerdo previo del owner, CI o publicación DRAFT.

**Disposición posterior (2026-11-25):** Ratificación arquitectónica expresa del owner, 2026-11-25, ante solicitud específica de aprobar ADR PPPR 02 v0.1.0 en calidad de autoridad arquitectónica del proyecto: «Si, estoy de acuerdo. adelante con eso». Objeto ratificado: commit `070d8e43a272222756671f154b5c203192793be3`, blob `b2ce91e9878e8c2e807831817e32c6f9dd61a572`. Se registra el acto comunicado directamente en conversación; no se atribuye revisión formal GitHub, firma externa ni dictamen independiente de otro Board. Staff favorable; el owner ejerce la autoridad arquitectónica para esta decisión focal. No constituye aprobación científica ni autorización de datos, proveedor, coste, host, activación o merge. Se actualizan exclusivamente marcas documentales de estado y se registra la decisión; el contenido material ratificado permanece el de v0.1.0, recuperable por el blob original. La solicitud anterior queda satisfecha por esta ratificación; ejecución y cierre real permanecen pendientes según Plan. No se declara FROZEN este ADR por inferencia ni se modifica otro FROZEN.
