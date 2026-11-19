# PDF→PDF Product Readiness — entrada documental de la etapa

**Estado:** GOBERNANZA EN CONSTRUCCIÓN — Fase 0 en curso; PPPR.0.1 está FROZEN, pero todavía no están cerradas la auditoría global, la gobernanza ni la planificación aprobada. `PRODUCT_READINESS=PASS` NO acreditado.  
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

**Nota de nomenclatura y alcance:** el owner fijó la convención **`HITO_PPPR.0.x_{NOMBRE_DISTINTIVO_CORTO}.md`** el 2026-11-19. `PPPR` identifica una iniciativa transversal fuera de la numeración del roadmap, no una fase nueva. Se conserva la carpeta `pdf-pdf-product-readiness/00-foundation/`; la metodología general y la canónica de HITOs siguen aplicando, sin modificarlas ni derogar su prelación. Los IDs internos ya registrados del 0.1 no se reasignan. Conforme a §6.7 de la metodología general, los HITOs de Fase 0 se integrarán en `main` tras concluir esa auditoría. **En esta etapa se retendrá el PR general #66 en Draft hasta completar además el paquete documental de gobernanza**; los HITOs FROZEN se revisan incrementalmente mediante PR internos hacia la rama de gobernanza, sin declararlos integrados en `main` antes de tiempo.

## 4. Estado documental y secuencia canónica

1. **Fase 0 — auditoría forense:** HITOs `HITO_PPPR.0.1`…`PPPR.0.9` previstos, cada uno con evidencia, alcance y cierre conforme a la metodología de HITOs. El [PPPR.0.1](00-foundation/HITO_PPPR.0.1_RUTA_Y_PERIMETRO.md) está **FROZEN v1.0.9**; el número y partición de los restantes solo se ajustan si la evidencia lo exige. Los grafos e instrumentos temporales no se incorporan al repo. Fase 0 **NO está cerrada**.
2. **Después del cierre forense:** construir y aprobar el **ADR Maestro**; ADR de sub-fase **solo si hace falta**; y los **NADR necesarios**, con trazabilidad a las evidencias, reglas existentes y decisiones. No se crean documentos redundantes ni se reemplazan NADRs FROZEN ajenos a esta iniciativa.
3. **Después de los NADR aprobados:** crear y aprobar **un único Execution Plan vivo** con tareas, secuencia, dependencias, gates y referencias a reglas, sin introducir una matriz paralela de implementación. La existencia de un borrador no autoriza implementar.
4. **Gate documental de gobernanza:** mantener el [PR #66](https://github.com/RDsanchez-git/translator_pdf/pull/66) como **Draft** hasta que estén completos, revisados y aprobados los artefactos aplicables de auditoría, ADR/NADR y Execution Plan. Solo entonces presentar el PR general para revisión final y, previa aprobación explícita, integrar el paquete documental a `main`.
5. **Implementación posterior:** únicamente tras tener las decisiones normativas y el Execution Plan aprobados **e integrados a `main`**. La implementación usa PR de código independientes desde `main` y sigue DoR, DoD, CI, Exit Review Evidence Log y Deferred Findings Register según la metodología. Los artefactos de revisión propios de la ejecución se producen en sus gates, **no** se inventan como prerrequisito documental de esta fase.

No se crean carpetas vacías para `ADR/`, `NADR/`, `plans/`, `reports/`, `reviews/` ni `handoff/`: cada carpeta aparece con su primer artefacto legítimo.

## 5. Política Git para gobernanza PPPR

**Ramas y destino:**

- `main`: única rama de **integración definitiva**. No se modifica durante la preparación documental de PPPR.
- `pdf-pdf-product-readiness`: **rama temporal de integración de gobernanza** de toda la iniciativa (Fase 0 + ADR/NADR + Execution Plan). Es el `head` del **PR #66 Draft hacia `main`**, no una rama permanente de producto. Su nombre actual ya identifica la iniciativa; **no se renombra mientras #66 esté abierto**, para conservar ese PR y sus revisiones.
- `pppr/hito-0.2`, `pppr/hito-0.3`, …: ramas **cortas**, nacidas de la última versión de `pdf-pdf-product-readiness`; cada una presenta su propio PR **hacia la rama de gobernanza**, no a `main`. Se revisa, integra y elimina **antes de iniciar la siguiente**, evitando cadenas de PR apilados. `PPPR.0.1` ya se encuentra en la rama general.
- Tras completar la auditoría: ramas cortas separadas para `ADR Maestro`, los ADR de fase que realmente apliquen, `NADR` necesarios y `Execution Plan`, **en el orden metodológico**, con PR individuales hacia la rama de gobernanza. No se adelantan decisiones ni implementación.
- Una vez aprobado el paquete documental completo, **un solo merge final del PR #66 a `main`**, con estrategia que preserve la trazabilidad de commits/hitos si las reglas del repositorio lo permiten. Eliminar luego la rama general y las ramas auxiliares ya integradas.

**Reglas:** la secuencia real se registra en commits y PR revisados, no en ramas históricas retenidas; no se reutilizan nombres de ramas antiguas ni se hace merge automático; cada PR interno parte de la rama de gobernanza actualizada y se integra antes de abrir el siguiente. Los HITOs pueden estar FROZEN en la rama de revisión sin implicar integración en `main`. No se toca el workspace local del owner, SQLite, oráculos ni corpus. Se mantiene la precedencia de la metodología general y el carácter read-only de la auditoría.

## 6. Condición de salida de la Fase 0 (prerregistro de auditoría; no DoD de producto)

La auditoría deberá permitir: identificar sin ambigüedad **entrada → publicación**, enumerar consumidores y responsabilidades de cada frontera, vincular cada brecha confirmada con evidencia y obligación vigente o meta de producto, diferenciar capacidades existentes y desconectadas, registrar explícitamente incertidumbres no verificables, y obtener un conjunto de decisiones candidatas y dependencias suficientemente delimitado para gobernanza posterior. No se declara Fase 0 cerrada hasta disponer de esa trazabilidad, cobertura auditada y revisión metodológica. No se medirá éxito por número de documentos producidos.
