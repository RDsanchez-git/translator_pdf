# Convergencia PDF→PDF: documentación vigente

**Estado:** convergencia operativa acreditada en laboratorio con proveedor simulado; integrada a pipeline_stabilization el 2026-11-13 mediante [PR #46](https://github.com/RDsanchez-git/translator_pdf/pull/46) y merge commit [6818e86](https://github.com/RDsanchez-git/translator_pdf/commit/6818e86e21b14e77a606f0c863e9c199b4627601).

Esta es la **puerta de entrada documental vigente** a la ruta única. No es una aprobación de producción, de traducción real ni de fidelidad STEM. Los documentos históricos de 00-foundation conservan su fecha y valor probatorio; no deben utilizarse como instrucciones de operación vigentes.

## Lectura recomendada

1. [ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md](ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md): Atlas de ruta implementada, diagramas, archivos, contratos, persistencia, riesgos y mapa de cambios.
2. [LABORATORIO_Y_REPRODUCCION.md](LABORATORIO_Y_REPRODUCCION.md): sandbox, controles, comandos y límites de reproducción.
3. [EVIDENCIA_Y_CIERRE.md](EVIDENCIA_Y_CIERRE.md): actas, identidades, DoD y merge.

## Jerarquía

Las decisiones D-1/D-2 fueron aprobadas por el owner el 2026-11-08; sus antecedentes están en [Decisión D-1/D-2](../00-foundation/DECISION_CANDIDATE_CONVERGENCIA_PDF_PDF_D1_D2_20261105.md). El [Plan C0–C4](../00-foundation/PLAN_IMPLEMENTACION_CONVERGENCIA_OPERATIVA_UNICA_PDF_PDF_V1_20261109.md) queda como **registro de implementación cumplida**, no backlog activo. La [matriz R1/R2/R3](../00-foundation/MATRIZ_VERSIONADA_COMPOSICION_DISPOSICION_R1_R2_R3_V1_20261109.md) sigue siendo el inventario de consumidores y disposiciones. Los NADR FROZEN conservan autoridad propia; ninguna de estas guías los redefine.

## Separación de estados

- Acreditación de topología/control PDF→PDF con fake: **COMPLETADO**.
- Integración del código en pipeline_stabilization: **MERGED**.
- Despliegue/cutover, proveedor real, compatibilidad de SQLite legacy: **NO AUTORIZADOS POR ESTE CIERRE**.
- Fidelidad científica y lingüística, W09, corpus CI/B02: **trabajos independientes pendientes**.
- Consumidores externos de R1/R3: **UNKNOWN**, no eliminación autorizada.

El antiguo Atlas IN_PROGRESS, el Charter DRAFT, las actas I0 y los diseños L0 son piezas del expediente forense, no la guía de uso de la nueva ruta. Ver también la [guía FROZEN de organización arquitectónica](../../../README.md), que reserva 00-foundation para evidencia forense y handoff para entregas.
