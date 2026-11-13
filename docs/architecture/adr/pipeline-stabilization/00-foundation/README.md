# 00-foundation — índice del expediente forense e histórico

**Estado del frente:** convergencia C0–C4 completada y fusionada a pipeline_stabilization mediante [PR #46](https://github.com/RDsanchez-git/translator_pdf/pull/46), merge commit 6818e86e21b14e77a606f0c863e9c199b4627601.

**ENTRADA VIGENTE PARA LA RUTA PDF→PDF:** [handoff/README.md](../handoff/README.md). Este directorio es el **archivo histórico de auditoría, decisiones y planes ejecutados**, no el runbook actual de producción ni del sandbox. Una cabecera interna DRAFT, NOT_EXECUTED o IN_PROGRESS describe el **sujeto de su época**, no revoca el cierre posterior de C0–C4 ni convierte un borrador en norma FROZEN.

## Piezas de fundamento que deben conservar trazabilidad

| Documento | Función y tratamiento después del merge |
|---|---|
| [Decisión D-1/D-2](DECISION_CANDIDATE_CONVERGENCIA_PDF_PDF_D1_D2_20261105.md) | **Conservar como fuente de decisión aprobada por el owner** en su cabecera del 2026-11-08. Las secciones de candidatura y gates históricos describen el corte 2026-11-05, no decisiones nuevas. |
| [Plan de implementación](PLAN_IMPLEMENTACION_CONVERGENCIA_OPERATIVA_UNICA_PDF_PDF_V1_20261109.md) | **Conservar como plan ejecutado/cerrado**: C0–C4, DoD 9/9, sujeto del merge y testigos. NO copiar su antiguo checklist a nuevos planes activos. |
| [Matriz de composición R1/R2/R3](MATRIZ_VERSIONADA_COMPOSICION_DISPOSICION_R1_R2_R3_V1_20261109.md) | **Conservar como inventario de 94 filas** y disposiciones de compatibilidad/censo. NO interpretar NO_PRODUCTIVO o RETIRE_CANDIDATE como autorización de borrado. |
| [Atlas de ejecución](PRODUCTION_PIPELINE_EXECUTION_ATLAS.md) | **Archivo forense AS-IS de gran detalle**, versión 0.2.16 IN_PROGRESS. No usar como especificación de la ruta vigente; conserva cronología, comparaciones R1/R2/R3, referencias a normas y falsadores. |
| [Charter de auditoría](PIPELINE_STABILIZATION_AUDIT_CHARTER.md) | **Fuente histórica de preregistro**, v0.1.0 DRAFT. No reetiquetar como FROZEN ni destruir por haberse integrado C0–C4. |
| [Sandbox histórico R2 C/L1](SANDBOX_GOBERNANZA_Y_GUIA_OPERATIVA.md) | **Archivar como guía de testigo antiguo** (2026-11-03); fue superado como manual diario por [LABORATORIO_Y_REPRODUCCION](../handoff/LABORATORIO_Y_REPRODUCCION.md). No es equivalente al sandbox nuevo. |

## Candidatos a retirar de la navegación activa, NO a borrar sin censo

Los siguientes documentos describen instrumentos históricos en DRAFT, propuestas no ejecutadas o cierres acotados anteriores a la ruta única. Se conservarán en este primer PR de limpieza; su retiro físico requeriría verificar referencias entrantes, firmas SHA de custodia, obligaciones metodológicas y un plan de archivo con redirecciones.

- E2E_0_PREFLIGHT_AND_EVIDENCE_PLAN_DRAFT.md
- L0_AUDIT_SANDBOX_DESIGN_AND_VERIFICATION_SPEC_DRAFT.md
- L0_D1_REPRODUCIBLE_BUILD_AND_AUDIT_HARNESS_CONTRACT_DRAFT.md
- L0_D1_BUILD_PROVENANCE_MANIFEST_TEMPLATE.json
- L0_PF08_PF09_ISOLATION_EGRESS_REVIEW_DRAFT.md
- L0_HV_D1_R2_DICTAMEN_CONSOLIDADO_POST_HV15_20261102.md
- I0-1B_REGISTRO_HISTORICO_TECNICO_CANONICO.md **y su .sha256**
- I0-1C_ACTA_CIERRE_TECNICO_ACEPTADA_2026-10-22.md **y su .sha256**
- I0-1D_ACTA_CIERRE_TECNICO_ACOTADO_ACEPTADA_2026-10-31.md **y su SHA256.txt**
- I0-1E_ACTA_CIERRE_TECNICO_ACOTADO_ACEPTADA_20261101.md
- I0-1F_ACTA_CONSOLIDADA_CIERRE_TECNICO_ACOTADO_20261102.md

**No son basura**, aun cuando no deban figurar como documentación viva: algunas actas incluyen sujetos y evidencias con custodia y las plantillas contienen propuestas históricas citables. Borrarlas sería una decisión separada a la convergencia.

## Observaciones de trabajo

El subdirectorio [working-observations](working-observations/) contiene **11 registros históricos** de B03, W06, W08 y otras caracterizaciones. No equivalen a tareas abiertas de convergencia ni deben suprimirse por nombre. La compatibilidad legacy y los estudios científicos posteriores usan antecedentes en esos registros.

## Política editorial

1. **Un solo Atlas de ruta operativa vigente:** [handoff/ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md](../handoff/ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md).
2. **Un solo runbook del laboratorio vigente:** [handoff/LABORATORIO_Y_REPRODUCCION.md](../handoff/LABORATORIO_Y_REPRODUCCION.md).
3. **Una sola entrada a las actas finales:** [handoff/EVIDENCIA_Y_CIERRE.md](../handoff/EVIDENCIA_Y_CIERRE.md); evidencias fuente permanecen en GitHub PR #46.
4. No alterar oráculos/NADR FROZEN, no reescribir actas de evidencia para que «parezcan» actuales, no eliminar firmas de SHA, ni convertir el PR de documentación en remediación de CI o del runtime.
