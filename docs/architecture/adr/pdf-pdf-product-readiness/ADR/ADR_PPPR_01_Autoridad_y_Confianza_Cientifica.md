# ARCHITECTURE DECISION RECORD (ADR)
## ADR PPPR 01 (identificador candidato): Autoridad y confianza científica

* **Estado:** DRAFT — propuesta Staff, sin aprobación arquitectónica definitiva ni científica.
* **Versión:** 0.1.0.
* **Fecha de Emisión:** 2026-11-24.
* **Autor:** Staff Engineering / PPPR.
* **Fase Parent:** PDF→PDF Product Readiness (PPPR, iniciativa transversal; no nueva fase ROADMAP).
* **Baseline auditada:** `c773675e6f39fdc741de843bc9a5a01a4f2531a0`.
* **Evidencia Forense Vinculante:** HITO PPPR.0.8 E-0.8-006/014/020/021/026/046/047, DQ-0.8-02/03/04/05/06/07; PPPR.0.9 E-0.9-016…019; issue #34.
* **Referencias Cruzadas:**
  * **Depende de:** [ADR_PPPR_MASTER.md](ADR_PPPR_MASTER.md), DC-09/10/11/12, FROZEN.
  * **Implementado por (obligaciones existentes, sin nueva norma):** [NADR-FPPPR-01](../NADR/NADR_01_Conformidad_Cientifica_PDF_EN_ES.md), especialmente §5.2 R4–R6 y §8.
  * **Ejecutado por:** [Execution Plan único](../plans/PHASE_PPPR_EXECUTION_PLAN.md) §1.2.2, §2.6.1, §2.6.3.
  * **Protocolo subordinado candidato:** [PPPR_SCIENTIFIC_EVALUATION_PROTOCOL.md](../plans/PPPR_SCIENTIFIC_EVALUATION_PROTOCOL.md), DRAFT v0.1.0.
  * **Conflictúa con:** atribuir autoridad científica a la producción del PDF, a un hash, a CV histórica o a la mera aprobación arquitectónica.

> **Nota de gobernanza:** particulariza DC-09 sin modificar ni reemplazar al Maestro o NADR FROZEN. Nombre y ubicación candidatos conforme a 3_METH_ADR_SUBPHASES.md; se solicita ratificación. No autoriza efectos externos.

## 1. CONTEXTO Y JUSTIFICACIÓN

El sujeto PPPR es el PDF final EN→ES de la ruta soportada. HITO PPPR.0.8 E-006 y E-0.9-016 demuestran la diferencia frente a CV PDF→AST; E-020/021 y E-0.9-018 delimitan los testigos fake y de publicación. DQ-02/03/04 identifican ausencia de referencias bilingües acreditadas, independencia experimental y evaluación de fidelidad STEM y visual; DQ-06/07 delimitan herramientas heredadas, no incidentes de producto.

NADR-FPPPR-01 §5.2 obliga a consumir políticas de autoridad e independencia y criterios aprobados antes de evaluar, pero expresamente no crea ese modelo. DC-09 reserva una decisión arquitectónica previa para un modelo nuevo; DC-11 excluye adopción inicial de los subtools históricos. El Audit First 6.1.1 sobre la baseline no acreditó política aplicable; PR94 integrado, G1–G5 cerrados en sus alcances, 25/30 Tasks DONE, issue #34 OPEN, CV FAIL/DEFERRED, PRODUCT_DISPATCH=BLOCKED y PRODUCT_READINESS=NOT_CERTIFIED. No se deduce defecto científico ejecutado ni nuevo GAP P1.

El owner comunicó un dictamen Board favorable al enfoque, con resolución arquitectónica previa obligatoria: acepta la auditoría y solicita ADR complementario y protocolo concretos DRAFT. No equivale a aprobación de estos borradores, nombramiento de experto, acto externo firmado o review formal GitHub. Las fuentes técnicas públicas justifican el método en el protocolo, no autoridad sobre PPPR.

## 2. PROBLEMA ARQUITECTÓNICO

La legitimidad de un dictamen exige distinguir (a) autorización de acceso, (b) decisión arquitectónica, (c) competencia científica y (d) evidencia independiente del productor. Si se confunden, un mecanismo técnicamente correcto puede admitir un oráculo sin fundamento, criterios elegidos retrospectivamente o un dictamen autovalidado.

Dimensiones estructurales: autoridad y atribución; independencia por procedencia; separación entre aprobación y ejecución; límites de generalización y vigencia. La consecuencia de la ausencia de cualquiera de las precondiciones de autoridad aplicables es impedir certificación positiva, sin fabricar rechazo científico. Las consecuencias concretas y reglas de resultado son las ya vigentes de NADR-FPPPR-01.

## 3. DECISIÓN ARQUITECTÓNICA

**Candidata:** La confianza científica de PPPR se constituye mediante competencia humana acreditable y evidencia autorizada de procedencia independiente de la generación candidata, bajo un modelo aprobado por la autoridad arquitectónica y criterios científicos concretos aprobados previamente por autoridad competente, con atribución y alcance verificables.

En consecuencia:
* El owner controla permisos, custodia, tratamiento, recursos y alcance; el Architecture Board aprueba el modelo de confianza; ninguna de esas funciones por sí sola acredita competencia científica.
* Una autoridad científica humana acreditada por alcance valida referencias, métodos, criterios y suficiencia; evaluadores autorizados aplican el protocolo dentro de su competencia. Una persona puede cubrir varios roles o dimensiones si acredita competencia e independencia, sin autodesignación ni autovalidación del productor. La autoridad puede ser una persona o un conjunto de personas con cobertura explícita, no se exige crear organizaciones.
* Staff Engineering implementa controles y trazabilidad; pipeline produce candidatos. Ni IA, ni Staff, ni owner ni Board adquieren autoridad científica por la mera etiqueta del rol.
* La independencia deriva del origen, historia y separación de evidencia respecto del candidato y su ajuste. El documento fuente puede ser referencia directa para STEM y estructura, y se exigen referencias EN→ES elegibles para la dimensión lingüística. No se fuerza un solo GT para las tres dimensiones.
* Comprobaciones deterministas son apoyo cuando su alcance está demostrado; revisión científica competente resuelve las propiedades no decidibles por ellas. Autovalidación, segundo LLM sin independencia demostrada, CV de extracción y métricas agregadas no constituyen autoridad.
* El protocolo subordinado contiene las definiciones operacionales versionadas; la aprobación arquitectónica del modelo no sustituye la aprobación científica de su contenido ni los permisos efectivos.

## 4. OBJETIVO DE LA SUBFASE

Resolver el vacío de autoridad previsto por DC-09 y R4–R6 para que una evaluación del PDF final tenga fundamentos legítimos, previos y reproducibles, sin extender el alcance del producto ni crear una plataforma de benchmarking.

> La admisión de evidencia científica depende de autoridad, procedencia y criterios acreditables; ninguna herramienta se confiere a sí misma autoridad.

## 5. ALCANCE Y NO-OBJETIVOS

**Dentro:** constitución y límites de autoridad científica, independencia de referencias, separación de aprobación y ejecución, protocolo subordinado con criterios versionados y alcance científico declarado.

**Fuera:** elegir proveedor, activar dispatch, obtener corpus, evaluar candidatos, diseñar dictamen de Wave 6.2, cambiar baseline o GT históricos, reparar preflight/post-run legacy, introducir servicios, PKI, bases de datos, evaluadores LLM, fase ROADMAP o NADR adicional sin obligación nueva demostrada. No promete cobertura comercial universal ni conformidad ISO.

## 6. GOBERNANZA DE LA SUBFASE

Se preservan las invariantes DC-04/05/06/09/10/11/12 del Maestro; las obligaciones de implementación permanecen en NADR-FPPPR-01 R1–R11. El presente ADR candidato particulariza el modelo reservado por §8, no promulga nuevas reglas RFC 2119 ni cambia las 40 reglas PPPR o sus Tasks. Las condiciones de aceptación científicas pertenecen al protocolo subordinado y requieren aprobación competente. Las autorizaciones de custodia, egress, coste y host conservan su autoridad propia.

La atribución de competencia y aprobación se materializa mediante evidencia verificable, no roles autodeclarados. El owner y Board acreditan la identidad/mandato y revisan evidencia de competencia sin sustituir el juicio científico; autoridad científica competente valida el protocolo. Cualquier persona con más de un rol declara conflictos y demuestra separación respecto de generación/ajuste. Si no existe autoridad suficiente, el camino certificante queda bloqueado.

## 7. ARQUITECTURA OBJETIVO (TARGET STATE)

```text
Owner: permisos/custodia       Board: modelo de confianza aprobado
             |                              |
             +------ autoridad científica acreditable ------+
                                      |
                 referencias elegibles + protocolo previo
                                      |
Fuente EN -> ruta PPPR -> PDF final ES | evidencia independiente
                           |          |
                           +-- evaluación competente --+
                                      |
                         resultado por dimensión atribuible
```

La admisibilidad precede a la evaluación; admitir no certifica. Las tres dimensiones son necesarias para conformidad integral, sin compensaciones; una negativa válida no equivale a incompletitud. La evidencia histórica conserva su sujeto y vigencia. Las fronteras de implementación y secuencia pertenecen al Execution Plan.

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación | Bidireccional |
|---|---|---|
| ADR_PPPR_MASTER.md | Particulariza DC-09; conserva DC-10/11/12 | Subordinación prevista por DC-09; sin editar FROZEN |
| NADR-FPPPR-01 | Consume modelo/política aprobados según §5.2 y §8 | Enlace existente genérico a política futura; no afirmar nueva reciprocidad FROZEN |
| PPPR_SCIENTIFIC_EVALUATION_PROTOCOL.md | Protocolo subordinado, no normativa técnica ni plan paralelo | Sí, ambos DRAFT |
| PHASE_PPPR_EXECUTION_PLAN.md | Secuencia única, Task 6.1.1 y consumidores posteriores | Referencia existente a política previa; vínculo específico pendiente aprobación/reconciliación LIVING |
| HITO PPPR.0.8 / 0.9 | Evidencia forense, no decisión | No modificar |

Cualquier nueva dependencia normativa real que no esté cubierta se tramitará conforme a 4_METH_NADR.md §8, antes de implementarla; no se declara aquí.

## 9. RELACIÓN CON LA METODOLOGÍA DE GOBERNANZA

Conforme a 1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md §§2, 3.2, 6.2 y 9.1 y 3_METH_ADR_SUBPHASES.md, este ADR define exclusivamente QUÉ y POR QUÉ. El protocolo versionado expresa la política científica aplicada; los NADR FROZEN gobiernan obligaciones técnicas; el único Execution Plan gobierna secuencia y DoD. No se crea un plan paralelo ni se modifica FROZEN.

**Solicitud de revisión:** aprobar o rechazar el modelo arquitectónico y nomenclatura, verificar si el protocolo candidato queda científicamente defendible y si existe autoridad humana acreditable. DRAFT no otorga vigencia. Sin aprobación efectiva y previa de modelo/protocolo, 6.1.1 no se cierra; 6.1.2–6.2.2 permanecen sin iniciar. No merge intermedio.
