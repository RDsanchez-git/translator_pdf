# Ruta operativa única PDF→PDF — documentación vigente

**Estado:** integrada en `pipeline_stabilization` mediante [PR #46](https://github.com/RDsanchez-git/translator_pdf/pull/46) (código) y [PR #47](https://github.com/RDsanchez-git/translator_pdf/pull/47) (documentación). `CONVERGENCIA_OPERATIVA_ACREDITADA` significa **topología/control PDF→PDF probado en laboratorio con fake**, no `PRODUCT_READINESS=PASS`.

## Tres referencias definitivas

1. [ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md](ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md) — arquitectura implementada, diagramas, archivos y símbolos, identidades, FSM, autoridad, recuperación y matriz de impacto de cambios.
2. [LABORATORIO_Y_REPRODUCCION.md](LABORATORIO_Y_REPRODUCCION.md) — Compose, sandbox, imagen y cachés pinneadas, preflight, comandos de ensayo, condiciones STOP y límites de reproducción.
3. [EVIDENCIA_Y_CIERRE.md](EVIDENCIA_Y_CIERRE.md) — decisión final D-1/D-2, DoD 9/9, C0–C4, testigos, identidades, actas y merges.

**Esta carpeta es la única entrada documental vigente de la ruta PDF→PDF.** Cualquier cambio de una frontera del pipeline debe actualizar el Atlas y registrar la evidencia focal correspondiente; no volver a abrir un Atlas paralelo de R1/R2/R3.

## Decisión final implementada

- **D-1 (owner, 2026-11-08):** un único contrato de entrada PDF→PDF desde CLI. La arquitectura **sí** utiliza varios procesos especializados; no existen varios motores productivos seleccionados por los entrypoints soportados.
- **D-2:** continuidad OCR → G3 (`runtime/engine.py`) → G5 (`apps/compiler/__main__.py`) sobre planes, receipts y proyecciones durables. `translate --run` reutiliza esas clases en ambiente aislado, no es otro daemon de producción.
- El código de R1/R3 puede conservarse como biblioteca, test o benchmark sin convertirse en un root productivo. Llamadores externos al repositorio continúan `UNKNOWN`.

## Límites vigentes

No se acreditan aquí traducción lingüística real, fidelidad STEM/W09, proveedor comercial, todos los vectores/figuras/tablas, costos operativos, despliegue o cutover. La generación histórica `G3_EXTERNAL_UNKNOWN` **no autoriza reintento**. Los NADR FROZEN y la [guía general de arquitectura](../../../README.md) mantienen su autoridad.

**Simplificación documental:** los expedientes anteriores de investigación, planes ejecutados, variantes y laboratorios R1/R2/R3 salen del árbol actual de esta carpeta. Los hechos vigentes de decisión y acreditación permanecen consolidados en estos tres documentos y en los PR #46/#47; no es necesario conservarlos como guías competidoras.
