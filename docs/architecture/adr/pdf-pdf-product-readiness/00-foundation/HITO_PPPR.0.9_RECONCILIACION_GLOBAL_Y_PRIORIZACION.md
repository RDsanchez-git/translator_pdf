# HITO_PPPR.0.9_RECONCILIACION_GLOBAL_Y_PRIORIZACION.md

**Estado:** IN_PROGRESS v1.0.0  
**Fecha de apertura:** 2026-11-20  
**Congelamiento:** N/A  
**Iniciativa:** PPPR, auditoría forense de Fase 0 transversal (no fase nueva del roadmap)  
**Tipo:** Reconciliation HITO / Gap Matrix transversal  
**Mandato:** consolidar y reconciliar E/GAP/DQ/DC de PPPR.0.1–0.8 FROZEN, sin reabrir decisiones cerradas; distinguir identidad causal, propagación y observaciones históricas, ordenar riesgos por dependencia y entregar una base forense para ADR Maestro. **No** diseñar ni implementar.  
**Código de producto anclado:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`.  
**Baseline de gobernanza:** `pdf-pdf-product-readiness@10a95ebb3adf7a070dd70e047a59fae0814445cb`, con PPPR.0.1–0.8 FROZEN.  
**Jerarquía:** metodologías `docs/architecture/1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` v1.3.0 FROZEN y `docs/architecture/1.2_METH_FOR_FORENSIC_HITOs.md` v1.2.0 FROZEN; `PROJECT_SCOPE.md` y `ENGINEERING_PRINCIPLES.md`; D-1/D-2 y código seleccionado; ADR/NADR FROZEN **solo aplicables y compatibles**. Atlas de ruta única v1.0.2 como mapa descriptivo AS-IMPLEMENTED, no norma autónoma.  
**Método:** reconciliación documental read-only. **NOT_RUN**: pruebas, CI, Docker, Tectonic, proveedor, host Windows, SQLite de uso, corpus/GT privados o experimentos científicos.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-11-20 | Primera pasada de reconciliación 0.1–0.8: 270 E-IDs de origen, 14 GAP-IDs P1 OPEN heredados con un par causalmente duplicado, un GAP-ID histórico retirado, dos GAP-IDs candidatos no confirmados, 37 DQ-IDs y 22 DC-IDs registrados. Clasificación inicial de diferencias, propagaciones, hipótesis y dependencias para ADR. Sin GAP nuevo, pruebas ni FROZEN. |

## 1. RESUMEN EJECUTIVO

**Hallazgo central provisional:** la ruta única D-1/D-2 seleccionada (CLI→OCR→G3→G5→PDF) tiene continuidad operacional histórica con fake y contratos técnicos comprobables, **pero no certificación de traducción científica EN→ES**. Sus ocho HITOs de auditoría FROZEN registran 270 E-IDs, 14 GAP-IDs P1 activos de origen y preguntas de decisión/evidencia todavía pertinentes. Los **14 IDs no equivalen automáticamente a 14 causas independientes**: GAP-0.1-01 y GAP-0.4-02 observan la misma falta de conmutación física del modelo. El HITO 0.9 preserva ambos IDs y evita duplicar trabajo futuro.

**Dictamen inicial:** 14 GAP-IDs P1 OPEN heredados; tras ese único solapamiento confirmado, **13 unidades causales preliminares** (no se han descartado otras coincidencias). No se crean P1 nuevos, no se cierran GAP anteriores, no hay `PRODUCT_READINESS=PASS`. La futura prioridad ejecutiva corresponde al ADR Maestro y al plan aprobado, no a esta auditoría.

## 2. LÍMITE EPISTEMOLÓGICO / OBSERVED ≠ REQUIRED ≠ DECISION

- **Observed:** código de `main` pinneado, HITOs/PR integrados en rama general, inventarios y testigos *leídos*. Un PASS histórico es solo del SHA y sujeto que lo produjo. Issues #34 y #36 OPEN no acreditan defectos adicionales de la ruta convergida.
- **Required:** integridad STEM, trazabilidad, fórmula/código, jerarquía y fail-closed de `PROJECT_SCOPE`/principios; normas F18 para autoridad/efectos del runtime actual. Un NADR F17-BIS solo es aplicable si su estado es aprobado, su sujeto es compatible y no fue desplazado.
- **Decision:** owner fijó EN→ES y D-1/D-2; renovación de inferencia pendiente, no hay modelo/proveedor aprobado, gate científico, modalidad host ni solución de GAP aprobada.
- **HISTÓRICO:** NADR-F17BIS-06 está `PROPOSED`; P6 multirruta, bench Groq A/B y `FINAL_EVALUATION HARD_FAIL` no son estado científico del PDF traducido; pruebas C2/T07 son fake.
- **NO VERIFICABLE:** proveedor real, privacidad/egress, costo observado, host/Compose realmente activo, PDFs privados y calidad física, lingüística y científica de resultados. **Razón/no-bloqueo:** fuera de lectura estática y sin autorización/oráculos; no impide mapear causas, pero impide certificar producto. **Destino:** DQ originales, ADR Maestro y testigos autorizados en Execution Plan posterior.
- **Regla:** la autoridad de un GAP permanece en su HITO origen. Este documento no prescribe implementación ni crea otra fuente normativa.

## 3. ALCANCE AUDITADO

| Fuente previa | Estado | Superficie principal y límite |
|---|---|---|
| PPPR.0.1 v1.0.9 | FROZEN / RECONCILIADO | Roots, inventario, consumidores; no prueba ausencia de lanzadores externos |
| PPPR.0.2 v1.0.3 | FROZEN / RECONCILIADO | PyMuPDF, perfiles/geom; no PDFs científicos físicos ejecutados |
| PPPR.0.3 v1.0.3 | FROZEN / RECONCILIADO | AST, chunk/identidad; semántica de NADR-03 debe contrastarse con uso D-1/D-2 |
| PPPR.0.4 v1.0.3 | FROZEN / RECONCILIADO | G3, idioma EN→ES, presupuesto, modelo; no proveedor real |
| PPPR.0.5 v1.0.3 | FROZEN / RECONCILIADO | FSM/W06/leases/SQLite; no incidentes externos observados |
| PPPR.0.6 v1.0.5 | FROZEN / RECONCILIADO | G5/TeX, perfiles, PDFs; no compilación científica acreditada |
| PPPR.0.7 v1.0.5 | FROZEN / RECONCILIADO | Host/Compose, secrets, despliegue; host externo NO VERIFICABLE |
| PPPR.0.8 v1.0.4 | FROZEN / RECONCILIADO | CV, baseline, tests y ciencia; 0 GAP productivo propio nuevo |
| Código/CI/testigos primarios | REFERENCIADO | Reutilizar auditorías por SHA, no reinventariar todo `main` |
| ADR/NADR/Execution Plan PPPR futuros | FUERA DE ALCANCE | No decidir antes de cerrar Fase 0 |

## 4. FUENTES DE EVIDENCIA

**HITOs FROZEN canónicos:** los ocho `HITO_PPPR.0.{1…8}_*.md` en `docs/architecture/adr/pdf-pdf-product-readiness/00-foundation/` de la rama general. **E-IDs de origen por HITO:** 44 / 21 / 20 / 21 / 34 / 42 / 39 / 49, total **270**; mantienen individualmente sus estados y severidades.

**Código/contratos:** `main@1d21cfe`; `PROJECT_SCOPE.md` §§2/4; `ENGINEERING_PRINCIPLES.md` §§III/IV; D-1/D-2; Atlas `ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md`; NADR-F18 relevantes. **NADR históricos revisados:** NADR-F17BIS-03 `APPROVED/FROZEN` (identidad), NADR-F17BIS-06 `PROPOSED` (no obligatorio), NADR-F17BIS-09 `APPROVED/FROZEN` solo compatible para aislamiento físico G5 (§5.2; no trasladar Event Log §5.1 automáticamente frente a F18), NADR-F17BIS-16 FROZEN con semánticas de hash diferenciadas. **Issues:** #34 OPEN (custodia de 15 PDFs canónicos), #36 OPEN (texto anterior a convergencia posible). **Testigos históricos:** PR #46/C2/T07 con fake, TST-STAB #63/#64, CV extracción. No se ejecutó ninguno en 0.9.

## 5. MAPA DE RECONCILIACIÓN POR PRODUCTOR/CONSUMIDOR

```text
D-1/D-2: CLI -> OCR / AST -> G3 (contexto, proveedor, receipts) -> G5 -> PDF
               0.2/0.3           0.4/0.5                     0.6
                     0.7 = host/Compose/entornos; 0.8 = testigos/oráculos
                     0.9 = causas compartidas y decisiones pendientes
```

Una observación downstream de un mismo defecto upstream no autoriza otro GAP. La topología es lógica, no prueba de atomicidad FS/DB ni del proveedor elegido.

## 7. MATRIZ OBSERVED / REQUIRED / DECISION (CRUCES)

| Frontera | Observed | Required/contrato vigente | Decision pendiente |
|---|---|---|---|
| G3 inferencia/EN→ES | Conmutación lógica sin modelo físico, ventana fallback insuficiente, idioma no explícito y modelo retirado según 0.4 | Scope EN→ES, tipado explícito y fail-closed; no NADR-06 PROPOSED como MUST | Elección backend/modelo, idioma vinculante en request, presupuesto y fallback |
| Perfil/layout | Muestreo omite página y usa `612.0`, con efecto aguas abajo G5 | Linaje físico/geométrico, criterio visual a definir | Contrato por perfil + falsador focal tras autorización |
| AST y G5 | Firma no representa jerarquía, falta canonización; G5 pierde heading y usa TeX crudo para CODE/TABLE | Scope/principios; NADR-F17BIS-03 solo si su ámbito sigue siendo aplicable | Criterios de identidad/representación, sin NFKC o parser nuevos por presunción |
| W06/recuperación | UNKNOWN sin escalamiento, lease antes del semáforo, sweeper con inconsistencia declarada | F18 vigente y principios de autoridad/fail-closed | Reconciliación de mecanismos existentes y pruebas focales, no retry ciego |
| Host/CI/ciencia | Compose no acredita host; CV extrae AST, C2 fake | Producto comercial/ científico debe disponer de evidencia acorde al sujeto | Modalidad de operación, oráculos y gates independientes EN→ES |

## 10. REGISTRO DE EVIDENCIA FORENSE — PRIMERA PASADA

**P2 en 0.9** = evidencia de *reconciliación transversal*, no rebaja severidad P1 de los GAP-IDs de origen.

| E-ID | Sev | Evidencia Observed (fuente FROZEN) | Reconciliación / alcance |
|---|---|---|---|
| **E-0.9-001** | P2 | Ocho HITOs FROZEN, 44+21+20+21+34+42+39+49 E-IDs | **270 identificadores originales**, no 270 pruebas físicas |
| **E-0.9-002** | P2 | §§14 de 0.1–0.6 | **14 GAP-IDs P1 OPEN heredados**, cero nuevos en 0.7/0.8 |
| **E-0.9-003** | P2 | 0.1 E-002/GAP-01 y 0.4 E-002/GAP-02 | **MISMA CAUSA:** SWITCH_MODEL no cambia modelo físico |
| **E-0.9-004** | P2 | 0.4 E-019/GAP-04 | El límite fallback core+contexto es **DISTINTO** de SWITCH_MODEL físico |
| **E-0.9-005** | P2 | 0.4 E-001/013 y E-003/011/012 | Modelo retirado e idioma destino EN→ES omitido son obligaciones distintas |
| **E-0.9-006** | P2 | 0.2 E-011/GAP-01 | Muestreo no recibe página física correctamente |
| **E-0.9-007** | P2 | 0.2 E-012/GAP-02 y 0.6 E-028 | `612.0` es causa upstream y propagación downstream, no otro GAP |
| **E-0.9-008** | P2 | 0.3 E-010 y 0.6 E-026 | Firma AST jerárquica y presentación HEADING son **distintos contratos** |
| **E-0.9-009** | P2 | 0.3 E-020/GAP-02 y NADR-F17BIS-03/-16 | Canonización/identidad FROZEN heredada, sin imponer algoritmo Unicode |
| **E-0.9-010** | P2 | 0.6 E-025/GAP-01 | CODE/TABLE terminan como TeX crudo; requisito actual de preservación |
| **E-0.9-011** | P2 | 0.5 E-019/GAP-01 | UNKNOWN en cuarentena sin escalamiento conectado; no retry ciego |
| **E-0.9-012** | P2 | 0.5 E-020/GAP-02 | Lease no revalidado tras semáforo antes de efecto externo; no se observó doble gasto |
| **E-0.9-013** | P2 | 0.5 E-032/GAP-03, 0.7 §14 | Sweeper Compose: GAP de 0.5, no duplicar en 0.7 |
| **E-0.9-014** | P2 | 0.6 E-027/GAP-03 retirado | NADR-F17BIS-06 PROPOSED; NO ACTIVO |
| **E-0.9-015** | P2 | 0.7 §14 GAP-01/02 | Dos IDs candidatos NO CONFIRMADOS, no P1 del producto |
| **E-0.9-016** | P2 | 0.8 E-006/014/020/021 | CV extracción PDF→AST vs testigos OCR→G3(fake)→G5, sin fidelidad EN→ES |
| **E-0.9-017** | P2 | 0.8 E-001/002/003, issue #34 OPEN | 21 documentos/GT, 6 PDF Git, 15 faltantes; no sustituir |
| **E-0.9-018** | P2 | 0.8 E-026/046/047 y §14 v1.0.4 | Preflight/post-run históricos OBS P2, no GAP G3/G5 por herencia |
| **E-0.9-019** | P2 | 0.8 E-044/048/049 | NORMATIVE_DESIGN y HARD_FAIL históricos ≠ calibración o resultado del producto |
| **E-0.9-020** | P2 | 0.1–0.8 DQ/DC de origen | 37 DQ-IDs y 22 DC-IDs registrados; no son 59 tareas independientes |
| **E-0.9-021** | P2 | NADR-F17BIS-03/-06/-09, F18 y HITO 0.6 | Autoridad histórica por estado/ámbito, no traslado indiscriminado |
| **E-0.9-022** | P2 | 0.7 y 0.8 FROZEN, tests NOT_RUN | Host/ciencia/proveedor NO VERIFICABLE, no inferir PASS |
| **E-0.9-023** | P2 | PR #73 MERGED, PR #66 OPEN Draft, main intacta | PPPR sigue en gobernanza documental, no integración productiva |
| **E-0.9-024** | P2 | Issue #36 OPEN; HITO 0.3/0.5 | Issue histórico de W08 no constituye nuevo GAP por nombre |

## 12. TRIAJE — FAMILIAS DE RIESGO Y DEPENDENCIAS (NO PLAN)

| Familia | Evidencia dominante | Pregunta para ADR / límite |
|---|---|---|
| Calidad científica y corpus | 0.8 DQ/DC, issue #34 | ¿Qué sujeto/oráculo independiente EN→ES y garantía STEM? No inventar umbrales ni GT |
| Traducción funcional | GAP-0.4-01…04 + 0.1-01 (misma causa que 0.4-02) | Backend vigente, idioma, presupuesto/fallback; ninguna solución aprobada |
| Seguridad de efecto y estado | GAP-0.5-01…03 | UNKNOWN, lease, sweeper; conservar F18, evitar efecto duplicado |
| Linaje/documento | GAP-0.2-01/02, 0.3-01/02, 0.6-01/02 | Geometría, firma, TeX y headings; tests focales cuando estén autorizados |
| Modalidad comercial | 0.7 DQ/DC y candidatos no confirmados | CLI host/contenedor, mounts/secrets, observabilidad; entorno aún NO VERIFICABLE |
| Reutilización científica | 0.8 DQ-06/07 | Tooling F17-BIS solo tras verificar caller/contrato y sujeto |

El orden expone **dependencias**: no asigna waves, responsables, modelos ni tecnologías. La priorización ejecutiva y el Execution Plan siguen siendo futuros y requieren aprobación.

## 14. GAP MATRIX TRANSVERSAL (ESTADOS HEREDADOS)

| ID original | E-ID origen | Estado FROZEN | Reconciliación |
|---|---|---|---|
| **GAP-0.1-01** | 0.1 E-002 | **P1 OPEN** | MISMA CAUSA que 0.4-02; preservar ambos IDs |
| **GAP-0.2-01** | 0.2 E-011 | **P1 OPEN** | Perfil/muestreo page number |
| **GAP-0.2-02** | 0.2 E-012 | **P1 OPEN** | page width 612.0; E-0.6-028 solo propagación |
| **GAP-0.3-01** | 0.3 E-010 | **P1 OPEN** | AST hash sin jerarquía, no igual a render |
| **GAP-0.3-02** | 0.3 E-020 | **P1 OPEN** | Unicode/canonización; aplicabilidad NADR-03 pendiente |
| **GAP-0.4-01** | 0.4 E-001/013 | **P1 OPEN** | Modelo retirado según HITO |
| **GAP-0.4-02** | 0.4 E-002 | **P1 OPEN** | Dueño causal del cruce con GAP-0.1-01 |
| **GAP-0.4-03** | 0.4 E-003/011/012 | **P1 OPEN** | Destino EN→ES no explícito |
| **GAP-0.4-04** | 0.4 E-019 | **P1 OPEN** | Core+contexto puede exceder fallback |
| **GAP-0.5-01** | 0.5 E-019 | **P1 OPEN** | UNKNOWN sin escalamiento |
| **GAP-0.5-02** | 0.5 E-020 | **P1 OPEN** | Lease no revalidado tras semáforo |
| **GAP-0.5-03** | 0.5 E-032 | **P1 OPEN** | Sweeper Compose/estados/reporting |
| **GAP-0.6-01** | 0.6 E-025 | **P1 OPEN** | CODE/TABLE TeX crudo |
| **GAP-0.6-02** | 0.6 E-026 | **P1 OPEN** | HEADING en render (distinto hash AST) |

**Fuera del total activo:** GAP-0.6-03 **HISTÓRICO RETIRADO**, con E-0.6-027 conservada, por NADR-F17BIS-06 PROPOSED; GAP-0.7-01/02 **CANDIDATOS NO CONFIRMADOS** (secrets/montaje CLI host), sujetos a decisiones de modo y proveedor. PPPR.0.8 no añadió GAP productivo. **Conteo: 14 identificadores OPEN; 13 unidades causales preliminares tras un solo par duplicado verificado.** Ningún GAP antiguo se marca RESOLVED aquí.

## 15. HIPÓTESIS DE RECONCILIACIÓN — PRIMERA PASADA

| ID | Pregunta | Veredicto actual |
|---|---|---|
| **H-0.9-A** | ¿0.1–0.8 están FROZEN y main sin PPPR? | **CONFIRMADA**, por SHA y metadata |
| **H-0.9-B** | ¿0.1-01 y 0.4-02 son la misma causa? | **CONFIRMADA**, SWITCH_MODEL físico |
| **H-0.9-C** | ¿612.0 de 0.2 debe originar otro GAP G5? | **RECHAZADA**, solo propagación |
| **H-0.9-D** | ¿AST hash y HEADING G5 son un solo defecto? | **RECHAZADA**, contratos distintos |
| **H-0.9-E** | ¿GAP-0.6-03 sigue vigente? | **RECHAZADA**, retirado |
| **H-0.9-F** | ¿0.7-01/02 son P1 activos? | **RECHAZADA**, candidatos |
| **H-0.9-G** | ¿CV/bench F17-BIS certifica el PDF EN→ES? | **RECHAZADA como garantía**, 0.8 FROZEN |
| **H-0.9-H** | ¿37 DQ y 22 DC exigen resoluciones independientes? | **TO BE VERIFIED**, segunda pasada agrupará destinos |

## 16. DQ Y DC — TRANSFERENCIA PROVISIONAL

**37 DQ-IDs históricos:** 0.1=5, 0.2=4, 0.3=4, 0.4=4, 0.5=4, 0.6=4, 0.7=5, 0.8=7. En 0.1, DQ-04 y DQ-05 ya figuran **RESUELTAS**; el conteo no representa 37 asuntos abiertos. Hay referencias ya parcialmente reconciliadas por posteriores HITOs y deben deduplicarse por destino antes del cierre.

**22 DC-IDs históricos:** 0.1=0, 0.2=0, 0.3=3, 0.4=4, 0.5=3, 0.6=4, 0.7=4, 0.8=4. **No equivalen a 22 nuevos ADR ni decisiones ya aprobadas.** No crear DC adicionales solo por reagrupación.

**DQ-0.9-01 — pendiente de contraste, no bloquea inventario:** ¿qué partes específicas de NADR-F17BIS-03 FROZEN (hash de AST) aplican al uso actual de `compute_ast_hash` como identidad de generación D-1/D-2, y cómo se relacionan con NADR-F17BIS-16? **Motivo:** F17-BIS nació multirruta; el contrato no debe trasladarse íntegro sin cotejo. **No-bloqueo:** no se rebajan ni se resuelven GAP-0.3-01/02 FROZEN durante una reconciliación; el punto sí condiciona una futura decisión normativa de implementación. **Destino:** segunda pasada PPPR.0.9; ADR Maestro si sigue exigiendo decisión, NADR nuevo solo cuando una laguna se demuestre.

## 17. RECONCILIACIÓN HISTÓRICA Y NO-REGRESIÓN

- D-1/D-2 define el producto vigente. R1/R3, P6 F17-BIS, Event Log exclusivo anterior, pruebas fake y benchmark A/B son historia o herramientas delimitadas, no nuevas rutas.
- NADR-F17BIS-03 está APPROVED/FROZEN pero su **aplicabilidad fina** a D-1/D-2 queda en DQ-0.9-01; NADR-F17BIS-06 está PROPOSED, por eso GAP-0.6-03 retirado no revive; NADR-F17BIS-09 FROZEN aplica en aislamiento G5 compatible, no en exclusividad Event Log §5.1 frente a F18.
- E-0.8-026/046/047 son observaciones concretas sobre subtools históricos y no GAP productivos automáticos. Recibir booleano de provenance en núcleo puro es admisible si un caller prueba la verificación material; la biyección requiere cardinalidad/unicidad.
- Issue #34 sigue custodia autorizada de 15 PDFs. No fabricar hashes/GT, bajar threshold, inferir leakage ni equiparar HARD_FAIL topológico histórico con traducción actual. Issue #36 OPEN no prueba defecto nuevo en D-1/D-2 por título.
- Se mantienen todos los E/GAP IDs y veredictos FROZEN previos. Ninguna implementación ni suite científica se inició en este HITO.

## 21. CIERRE — IN_PROGRESS

**NO FROZEN — IN_PROGRESS v1.0.0.** Primera pasada global: 24 E-IDs P2 propios, 8 hipótesis (siete terminales, una TO BE VERIFIED), 14 GAP-IDs P1 **heredados** y cero nuevos, un par causalmente duplicado, un ID retirado, dos candidatos no confirmados; 37 DQ/22 DC de origen **registrados, no reconciliados completamente**. Ninguna prueba científica, proveedor, Tectonic, Docker ni CI ejecutados. No acreditar `PRODUCT_READINESS=PASS`.

**Pendiente para §8.1–8.2 y FROZEN:** contrastar DQ-0.9-01 con código/callers y norma compatible; cerrar H-0.9-H con triaje de destinos DQ/DC; revisar si existen otras relaciones causales y dejar prioridades dependientes de riesgo sin prescribir implementación. Después, emitir checklist, garantías positivas/negativas y gate explícito al ADR Maestro, sin abrir documentación paralela.

**Gobernanza:** un Markdown en rama corta `pppr/hito-0.9` nacida de `pdf-pdf-product-readiness@10a95ebb`; PR interno Draft hacia rama general. PR #66 permanece Draft a `main`. FROZEN metodológico y aprobación owner para merge son **gates separados**. Al integrar, verificar rama general, eliminar rama corta y recién entonces comenzar ADR Maestro desde nuevo HEAD.
