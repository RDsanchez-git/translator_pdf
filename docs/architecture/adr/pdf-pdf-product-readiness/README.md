# PDF→PDF Product Readiness — entrada documental de la etapa

**Estado:** IN_PROGRESS — apertura de Fase 0; no se ha aprobado un diseño ni se acredita `PRODUCT_READINESS=PASS`.  
**Fecha de apertura:** 2026-11-18.  
**Baseline de lectura:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`.  
**Naturaleza:** punto de navegación y delimitación del mandato, **no** ADR Maestro, NADR, Execution Plan ni evidencia forense.

## 1. Propósito y mandato

Investigar exhaustivamente —con profundidad proporcional al riesgo y con cobertura explícita— la ruta única PDF→PDF y sus dependencias, para determinar **qué existe, qué está conectado, qué es reutilizable, qué falta demostrar y qué realmente debe crearse o corregirse** antes de que el proyecto sea un traductor STEM utilizable. La auditoría puede cambiar las prioridades discutidas previamente; estas no se consideran decisiones de implementación.

Se conservan como punto de partida las decisiones de convergencia D-1/D-2 ya aprobadas: entrada soportada por CLI, OCR → G3 (`runtime/engine.py`) → G5 (`apps/compiler/__main__.py`), con planes y estado durables. No se crea una ruta productiva paralela. `CONVERGENCIA_OPERATIVA_ACREDITADA` significa laboratorio con fake; no certifica traducción lingüística, fidelidad STEM ni operación con proveedor comercial.

La meta final de esta etapa **no queda predeterminada por una lista de arreglos**: el ADR y el plan posteriores deberán delimitar, basados en la Fase 0, los hitos distinguibles de integración real, uso limitado y evaluación científica.

## 2. Perímetro obligatorio de investigación

La auditoría debe inventariar las superficies relevantes, incluyendo **módulos, entrypoints, factories, callers, persistencia, configuraciones y testigos**, sin suponer ausencia ni duplicación a partir de nombres de archivos:

| Superficie | Pregunta de auditoría |
|---|---|
| Ruta productiva y composición | Qué entrypoints están soportados; cómo se conectan OCR, G3, G5 y CLI; qué configuraciones efectivas usan |
| Ingesta, OCR/B02 y perfilado | Qué preserva, transforma, descarta o rechaza, incluidos vectores, lectura por columnas y gráficos |
| AST, normalización, segmentación y chunking | Cobertura lógica/física, tipos, matemática, identidades, snapshots y generación |
| G3, W06/W08, providers y prompts | Modelo, idioma, JSON, límites de contexto, fallback, cuota, presupuesto, caché, receipts e incertidumbre |
| FSM, SQLite, control/event/materialized planes | CAS, leases, epochs, recuperabilidad, publicación, persistencia y obligaciones F18 vigentes |
| G5, layout y compilación | Ecuaciones, tablas, imágenes, activos, Tectonic, degradación y salida física |
| Runtime y empaquetado | Docker/Compose, host Windows, bootstrap, cachés, redes, secretos, workspace y modo foreground |
| Tests, CI y verificación científica | Oráculos y falsadores, skips/deselected, alcances fake/real, corpus sellado y restricciones de custodia |
| Legacy y herramientas | Consumidores reales, contratos de compatibilidad, implementaciones desconectadas o históricas |

**Regla de cobertura:** se relevarán todos los entrypoints, componentes ejecutables y dependencias que puedan influir en la ruta seleccionada, y se distinguirá `AUDITADO`, `REFERENCIADO`, `NO_VERIFICADO` y `FUERA_DE_ALCANCE`. Exhaustividad del inventario **no** significa generar expedientes por cada archivo ni asumir que los tests prueban comportamiento físico.

**Exclusiones de la auditoría inicial:** cambios en producción, llamadas pagadas, lectura/transmisión de PDF privados, mutación de SQLite o del corpus/oráculos sellados, campañas nuevas de certificación, inventar nuevos motores o depurar componentes sin relación comprobada. El issue [#34](https://github.com/RDsanchez-git/translator_pdf/issues/34) permanece diferido por decisión del owner hasta autorización posterior.

## 3. Metodología y autoridad

Se aplican, con sus precedencias y estados FROZEN, los documentos existentes:

- [Metodología general](../../1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md): auditoría → ADR → NADR → Execution Plan → implementación → verificación → revisión; sin artefactos «por si acaso».
- [Metodología de HITOs](../../1.2_METH_FOR_FORENSIC_HITOs.md): evidencia `Observed ≠ Required ≠ Decision`, IDs estables, alcance, fuentes, gaps solo demostrados y criterio de cierre.
- [Guía de arquitectura](../../README.md), `PROJECT_SCOPE.md` y `ENGINEERING_PRINCIPLES.md`.
- [Handoff vigente de convergencia](../pipeline-stabilization/handoff/README.md), ADR/NADR FROZEN aplicables (incluida Fase 18), y [evidencia TST-STAB](../tests_stabilization/PLAN_REMEDIACION_TESTS_PIPELINE.md).

**Nota de nomenclatura:** `pdf-pdf-product-readiness` es el nombre de iniciativa expresamente seleccionado para esta etapa. La metodología emplea la convención `phase-{fase}` para fases numeradas: esta apertura **no declara haber creado una nueva fase numerada ni sustituye su ADR Maestro**. Si la gobernanza posterior requiere formalizarla como fase del roadmap, la autoridad correspondiente deberá resolver y registrar la relación con esa convención; no se elude la metodología por silencio.

## 4. Estado documental y secuencia

1. **Fase 0 en curso:** únicamente HITOs forenses bajo `00-foundation/`, con sus matrices e inventarios **dentro de esos HITOs**. Primer entregable: [HITO_0.1_RUTA_OPERATIVA_Y_PERIMETRO.md](00-foundation/HITO_0.1_RUTA_OPERATIVA_Y_PERIMETRO.md), `IN_PROGRESS`.
2. **Después de cerrar la auditoría:** sintetizar decisiones y emitir los ADR/NADR que correspondan, reutilizando obligaciones existentes antes de crear nuevas. Ningún Execution Plan se aprueba por adelantado.
3. **Después de la gobernanza:** un Execution Plan único y vivo ordenará tareas, gates, evidencias, PR, commits y estados.
4. **Al ejecutar:** tests y CI por SHA exacto, revisiones conforme a la metodología y handoff final con límites expresos.

No se crean carpetas vacías para `ADR/`, `NADR/`, `plans/`, `reports/`, `reviews/` ni `handoff/`. Se crearán solo cuando exista su primer artefacto legítimo.

## 5. Política Git de la etapa

- **Única rama de integración:** `main`.
- `pdf-pdf-product-readiness` es **solo la rama temporal de este primer PR documental**, no una rama acumuladora de toda la etapa.
- Cada entrega posterior parte del `origin/main` actualizado; un PR acotado, inicialmente Draft; aceptación y squash a `main`, o cierre sin merge si es rechazado.
- Tras integrar o rechazar, se elimina la rama temporal cuando corresponda. No apilar PR ni mantener ramas de fase largas.
- La continuidad reside en `main`, las evidencias de los HITOs, el plan vivo y los PR, no en ramas históricas.
- No tocar el workspace local del owner ni modificar/restaurar archivos locales ajenos al PR.

## 6. Condición de salida de la Fase 0 (prerregistro de auditoría; no DoD de producto)

La auditoría deberá permitir: identificar sin ambigüedad **entrada → publicación**, enumerar consumidores y responsabilidades de cada frontera, vincular cada brecha confirmada con evidencia y obligación vigente o meta de producto, diferenciar capacidades existentes y desconectadas, registrar explícitamente incertidumbres no verificables, y obtener un conjunto de decisiones candidatas y dependencias suficientemente delimitado para gobernanza posterior. No se declara Fase 0 cerrada hasta disponer de esa trazabilidad, cobertura auditada y revisión metodológica. No se medirá éxito por número de documentos producidos.
