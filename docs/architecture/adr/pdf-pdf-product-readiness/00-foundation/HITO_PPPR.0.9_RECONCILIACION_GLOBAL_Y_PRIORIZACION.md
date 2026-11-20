# HITO_PPPR.0.9_RECONCILIACION_GLOBAL_Y_PRIORIZACION.md

**Estado:** FROZEN v1.0.4  
**Fecha de apertura:** 2026-11-20  
**Congelamiento documental:** 2026-11-20  
**Iniciativa:** PPPR, auditoría forense de Fase 0 transversal (no fase nueva del roadmap)  
**Tipo:** HITO de reconciliación transversal **con Gap Matrix incorporada**; no sustituye ni redefine la plantilla compacta §11.2  
**Mandato:** consolidar y reconciliar E/GAP/DQ/DC de PPPR.0.1–0.8 FROZEN, sin reabrir decisiones cerradas; distinguir identidad causal, propagación y observaciones históricas, ordenar riesgos por dependencia y entregar una base forense para ADR Maestro. **No** diseñar ni implementar.  
**Código de producto anclado:** `main@1d21cfe958cc1de8a33824fed748cd6fe9260f42`.  
**Baseline de gobernanza:** `pdf-pdf-product-readiness@10a95ebb3adf7a070dd70e047a59fae0814445cb`, con PPPR.0.1–0.8 FROZEN.  
**Jerarquía:** metodologías `docs/architecture/1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` v1.3.0 FROZEN y `docs/architecture/1.2_METH_FOR_FORENSIC_HITOs.md` v1.2.0 FROZEN; `PROJECT_SCOPE.md` y `ENGINEERING_PRINCIPLES.md`; D-1/D-2 y código seleccionado; ADR/NADR FROZEN **solo aplicables y compatibles**. Atlas de ruta única v1.0.2 como mapa descriptivo AS-IMPLEMENTED, no norma autónoma.  
**Método:** reconciliación documental read-only. **NOT_RUN**: pruebas, CI, Docker, Tectonic, proveedor, host Windows, SQLite de uso, corpus/GT privados o experimentos científicos.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-11-20 | Primera pasada de reconciliación 0.1–0.8: 270 E-IDs de origen, 14 GAP-IDs P1 OPEN heredados con un par causalmente duplicado, un GAP-ID histórico retirado, dos GAP-IDs candidatos no confirmados, 37 DQ-IDs y 22 DC-IDs registrados. Clasificación inicial de diferencias, propagaciones, hipótesis y dependencias para ADR. Sin GAP nuevo, pruebas ni FROZEN. |
| 1.0.1-IN_PROGRESS | 2026-11-20 | Segunda pasada focal: inspección de NADR-F17BIS-03/16 y consumidores efectivos de compute_ast_hash; tensión de contrato alternativo vs uso de generación sin rebajar GAP-0.3. Primera agrupación de DQ/DC por propietarios y estado; H-0.9-H rechaza multiplicación 37+22 por ID, sin declarar resueltos asuntos físicos. 30 E-IDs P2, 8 hipótesis con disposición terminal de la pregunta, una DQ-0.9 pendiente. Sin tests ni FROZEN. |
| 1.0.2-IN_PROGRESS | 2026-11-20 | Tercera pasada: disposición individual exacta de 37 DQ-IDs (2 resueltas en origen, 35 diferidas/delimitadas) y 22 DC-IDs (candidatos no aprobados; EN→ES y renovar inferencia predecididos parcialmente), con razón, no-bloqueo, destino y familia; §14 clasifica scope de familias sin alterar severidad/propiedad. DQ-0.9-01 diferida al ADR. Sin nuevas pruebas, GAP o FROZEN. |
| 1.0.3-FROZEN | 2026-11-20 | Cierre §8.1–8.2, §9.2–9.4 y estructura §11.2: Gap Matrix de 13 unidades causales preliminares/14 GAP-IDs P1 OPEN heredados con 10 columnas y Decision Scope; 30 E-IDs P2, 8 hipótesis terminales, 37 DQ dispuestas individualmente, 22 DC con destinos, DQ-0.9-01 explícitamente diferida; garantías, límites y transición al ADR Maestro sin implementación. |
| 1.0.4-FROZEN | 2026-11-20 | Corrección documental posterior a FROZEN: §1 elimina calificadores provisionales impropios del dictamen; cabecera, §14 y §21 aclaran que es un HITO de reconciliación con Gap Matrix incorporada, no cumplimiento literal de la plantilla compacta de cinco secciones; §16/§21 distinguen 37 DQ heredadas y DQ-0.9-01 nueva. Sin alterar evidencia, GAPs, decisiones ni pruebas. |

## 1. RESUMEN EJECUTIVO

**Hallazgo central:** la ruta única D-1/D-2 seleccionada (CLI→OCR→G3→G5→PDF) tiene continuidad operacional histórica con fake y contratos técnicos comprobables, **pero no certificación de traducción científica EN→ES**. Sus ocho HITOs de auditoría FROZEN registran 270 E-IDs, 14 GAP-IDs P1 activos de origen y preguntas de decisión/evidencia todavía pertinentes. Los **14 IDs no equivalen automáticamente a 14 causas independientes**: GAP-0.1-01 y GAP-0.4-02 observan la misma falta de conmutación física del modelo. El HITO 0.9 preserva ambos IDs y evita duplicar trabajo futuro.

**Dictamen de cierre:** 14 GAP-IDs P1 OPEN heredados; tras ese único solapamiento confirmado, **13 unidades causales preliminares** (no se han descartado otras coincidencias). No se crean P1 nuevos, no se cierran GAP anteriores, no hay `PRODUCT_READINESS=PASS`. La futura prioridad ejecutiva corresponde al ADR Maestro y al plan aprobado, no a esta auditoría.

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

## 10. REGISTRO DE EVIDENCIA FORENSE — RECONCILIACIÓN FINAL

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
| **E-0.9-025** | P2 | `NADR_03_Semantic_Hashing_Chunking_Segregation.md` §5.1 R1/R4 y §9 | Norma FROZEN de firma de AST exige posición jerárquica y normalización canónica, con frontera explícita diferente del hash global de baseline |
| **E-0.9-026** | P2 | `NADR-F17BIS-16_Cryptographic_Identity_Semantics_&_Chaining.md` §5.2 R4–8 | Coexistencia permitida de contratos de hash distintos si propósito/dimensiones documentados; canon de baseline incluye node_id, alternativa de comparación de parsers puede excluirlo |
| **E-0.9-027** | P2 | `core/ast/hashing.py::compute_ast_hash` declara contrato alternativo para parsers/topología, serializa `(type,content)` en orden; excluye `heading_level/depth` y no normaliza texto | Docstring describe propósito histórico de comparación, pero no acredita que ese sea su **único** consumidor vigente |
| **E-0.9-028** | P2 | `core/chunking/contextual_plan.py::prepare_contextual_plan` usa `compute_ast_hash(raw_ast)` como identidad original y guardia `W08_OCR_SEMANTIC_AST_DRIFT`; `core/ast/registry.py` usa `(document_id,ast_hash)` como clave y nombre de archivo durable | **Uso activo de hash alternativo como identidad de generación**; propósito declarado de comparación de parsers no agota su papel en D-1/D-2 |
| **E-0.9-029** | P2 | PPPR.0.1 §21.2: DQ-0.1-04/05 **RESUELTAS** en sus ámbitos; PPPR.0.2–0.8 §§15/21 mantienen motivos/destinos | Los 37 DQ-IDs no son 37 cuestiones pendientes: no reabrir resueltas ni suponer que las remitidas a 0.8 ya tienen oráculos nuevos |
| **E-0.9-030** | P2 | DC-0.3-01…03, DC-0.4-01…04, DC-0.5-01…03, DC-0.6-01…04, DC-0.7-01…04 y DC-0.8-01…04 | 22 DC-IDs representan decisiones candidatas de varias capas; la agrupación en familias no implica 22 NADRs, soluciones independientes ni aprobaciones |

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

## 14. GAP MATRIX TRANSVERSAL — VEREDICTO FROZEN

**Naturaleza documental:** esta matriz de diez campos está **incorporada al HITO de reconciliación PPPR.0.9**. La plantilla compacta de cinco secciones definida en §11.2 es específica del tipo documental *Gap Matrix* independiente; no se declara que este HITO híbrido reproduzca literalmente su estructura ni se introduce una plantilla alternativa. Se preserva un único artefacto de reconciliación, sin duplicar el inventario o crear una segunda fuente de autoridad.

**Unidad de consolidación:** una fila por **núcleo causal preliminar**, sin borrar ninguno de los 14 GAP-IDs heredados. Cada fila conserva el finding de origen, el comportamiento observado, el requisito que justificó su severidad en el HITO FROZEN y el **Decision Scope** de §7.2. Las severidades P1 son **heredadas**, no reclasificaciones nuevas; no atribuir incidentes físicos no observados. **Decision Record asignado** indica destino documental **PENDIENTE**, no un ADR aprobado.

### 14.1 Matriz de 13 unidades causales preliminares (§11.2)

| GAP-ID de origen | Componentes afectados | Finding / E-ID fuente | Estado actual observado | Requerimiento arquitectónico objetivo | Brecha identificada | Severidad heredada | Consecuencia arquitectónica demostrable / límite | Decision Scope | Decision Record destino |
|---|---|---|---|---|---|---|---|---|---|
| **GAP-0.2-01** | OCR→`NodeGeometryAdapter`, perfilado | 0.2 E-011/013 | `page_number` no llega al muestreo | Política `FirstPagesSamplingPolicy(max_pages)`, principios de índices físicos | No se respetan primeras páginas cuando `max_pages >= 1` | **P1 LOCAL OPEN** | Perfil no acotado; impacto en papers NOT_RUN | LOCAL | ADR Maestro PPPR → plan aprobado |
| **GAP-0.2-02** | OCR geometry→perfil→G5 | 0.2 E-012/017; 0.6 E-028 | `relative_center_x` usa ancho fijo `612.0` | Geometría relativa al ancho de página real, linaje físico | Clasificación de centro puede variar con formato de página | **P1 LOCAL OPEN** | Distorsión de perfil transferible; PDF físico NO VERIFICABLE | CROSS-CUTTING | ADR Maestro PPPR → plan aprobado |
| **GAP-0.3-01** | `compute_ast_hash`, contexto/plan | 0.3 E-010/012; 0.9 E-027/028 | Pre-image omite `heading_level/depth` | Identidad de generación con semántica y jerarquía acordadas; NADR-03 histórico según ámbito | Firmas iguales para jerarquías distintas con texto/tipo/orden iguales | **P1 LOCAL OPEN** | Identidad semántica insuficiente en frontera; DQ-0.9-01 conserva decisión de contrato | CROSS-CUTTING | ADR Maestro (identidad de generación, PENDIENTE) |
| **GAP-0.3-02** | OCR texto→AST hash | 0.3 E-020; 0.9 E-025–028 | `strip()` sin canonización Unicode anterior al pre-image | Determinismo semántico compatible STEM; NADR-03 FROZEN según sujeto | Equivalencias Unicode pueden tener firmas distintas | **P1 LOCAL OPEN** | Desalineación de identidad; algoritmo concreto NO DECIDIDO | CROSS-CUTTING | ADR Maestro (semántica canónica, PENDIENTE) |
| **GAP-0.4-01** | G3, modelo/proveedor | 0.4 E-001/013 | Modelo configurado retirado según HITO 0.4 | Backend vigente para producto EN→ES autorizado | Configuración de inferencia obsoleta | **P1 LOCAL OPEN** | Disponibilidad real no acreditada; sin call comercial | LOCAL | ADR Maestro (backend, PENDIENTE) |
| **GAP-0.1-01 ↔ GAP-0.4-02** | `PromptBuilder`, `GroqProvider`, presupuesto G3 | 0.1 E-002; 0.4 E-002; 0.9 E-003 | `SWITCH_MODEL` deja `envelope.model_name` sin conmutar | Contrato tipado y fail-closed: selección física consistente con presupuesto | Fallback lógico ≠ modelo enviado | **2 IDs P1 LOCAL OPEN; 1 causa** | Puede intentar primaria con ventana de fallback; no error HTTP observado | CROSS-CUTTING | ADR Maestro (política fallback, PENDIENTE) |
| **GAP-0.4-03** | CLI→OCR→prompt G3 | 0.4 E-003/011/012 | Destino `es` no transmitido explícitamente | Producto EN→ES ya fijado por owner, contrato explícito | Idioma objetivo no verificable en request | **P1 LOCAL OPEN** | Traducción a español no garantizada por el contrato; fake no prueba lengua | CROSS-CUTTING | ADR Maestro (contrato EN→ES, PENDIENTE) |
| **GAP-0.4-04** | `PromptBudgetCalculator`, builder | 0.4 E-019 | Fallback compara núcleo, admite contexto que excede ventana | Aceptación solo si total cabe en ventana real | `required_window_size` puede superar fallback | **P1 LOCAL OPEN** | Admisión lógica de request físicamente inviable; distinto de conmutación | LOCAL | ADR Maestro (presupuesto/fallback, PENDIENTE) |
| **GAP-0.5-01** | `queue.db`, W06/UNKNOWN, CLI | 0.5 E-019/022/026 | Cuarentena sin escalamiento recurrente conectado | F18 R11, recuperación supervisada sin retry ciego | UNKNOWN puede permanecer sin señal configurable | **P1 LOCAL OPEN** | Bloqueo indefinido lógico, no llamada duplicada observada | CROSS-CUTTING | ADR Maestro + F18 existente → plan |
| **GAP-0.5-02** | Lease, semáforo, provider I/O | 0.5 E-020/021 | Check lease previo a espera del semáforo | F18 R2, autoridad vigente al iniciar efecto externo | Falta revalidación durable inmediata al efecto | **P1 LOCAL OPEN** | Efecto podría iniciar con lease vencido; sin gasto medido | CROSS-CUTTING | ADR Maestro + F18 existente → plan |
| **GAP-0.5-03** | Compose sweeper, FSM/queue/receipts | 0.5 E-032/023; 0.7 §14 | Selectores/transición/reporting no concuerdan | F18 R8/R10, recuperación coherente y observable | Sweeper declara estados diferentes de los que consulta/transiciona | **P1 LOCAL OPEN** | Reparación/observabilidad no fiables bajo composición declarada; host NOT_RUN | CROSS-CUTTING | ADR Maestro + F18 existente → plan |
| **GAP-0.6-01** | G5 renderer CODE/TABLE | 0.6 E-025/013/032 | Contenido literal se incorpora como TeX sin protección contextual adecuada | Scope §4: código e identificadores intactos | Literal puede mutar o impedir compilar | **P1 LOCAL OPEN** | Preservación no garantizada; salida física NOT_RUN | LOCAL | ADR Maestro (contrato literal/TeX) → plan |
| **GAP-0.6-02** | G5 renderer HEADING | 0.6 E-026/014 | Nivel/profundidad descartados antes de TeX | Scope: jerarquía estética y linaje; principios IV | H1/H2/H3 no quedan representados con distinción exigible | **P1 LOCAL OPEN** | Aplanamiento representacional, **no** GAP de hash de 0.3 | CROSS-CUTTING | ADR Maestro (jerarquía/layout) → plan |

### 14.2 Estadísticas globales y exclusiones

| Indicador | Valor | Interpretación |
|---|---:|---|
| HITOs FROZEN de origen | 8 | PPPR.0.1–0.8, sin modificaciones retroactivas |
| E-IDs heredados | 270 | 44+21+20+21+34+42+39+49, sin contar de nuevo E-0.9 |
| GAP-IDs P1 OPEN heredados | **14** | 0.1:1, 0.2:2, 0.3:2, 0.4:4, 0.5:3, 0.6:2 |
| Duplicidad causal verificada | **1 par** | GAP-0.1-01 ↔ GAP-0.4-02, IDs conservados |
| Unidades causales preliminares | **13** | 14 IDs menos un solapamiento; no equivalen a 13 tareas aprobadas |
| GAP-IDs retirados / candidatos no confirmados | 1 / 2 | GAP-0.6-03 histórico; GAP-0.7-01/02 candidatos, **excluidos** de OPEN |
| GAPs nuevos por PPPR.0.8/0.9 | **0** | Observaciones P2 ≠ incumplimientos productivos nuevos |
| DQ-IDs heredados / resueltos en origen / diferidos | 37 / 2 / 35 | Disposición individual §16, diferidos no bloquean auditoría |
| DC-IDs heredados | 22 | Ningún mecanismo nuevo aprobado por 0.9 |

**No-regresión:** el GAP de geometría 0.2-02 se propaga a G5 sin generar un segundo ID; el hash jerárquico de 0.3-01 y el render HEADING de 0.6-02 son contratos distintos. `NADR-F17BIS-06` está `PROPOSED`, por lo que no revive `GAP-0.6-03`. Los dos candidatos de despliegue de 0.7 carecen de modalidad/proveedor aprobado. Las observaciones `E-0.8-026/046/047` de certificación histórica siguen P2 con DQ-06/07, no se convierten en GAP productivo.

**Estado:** todos los GAP originales siguen OPEN; ninguna reparación ni aceptación de riesgo ha sido aprobada. El ADR Maestro examinará **consecuencia, aplicabilidad y opciones mínimas**, no comenzará con 13 recetas técnicas. Esta Gap Matrix reconcilia la evidencia ya emitida; no introduce un segundo registro operacional de implementación.

## 15. HIPÓTESIS DE RECONCILIACIÓN — VEREDICTOS TERMINALES

| ID | Pregunta | Veredicto actual |
|---|---|---|
| **H-0.9-A** | ¿0.1–0.8 están FROZEN y main sin PPPR? | **CONFIRMADA**, por SHA y metadata |
| **H-0.9-B** | ¿0.1-01 y 0.4-02 son la misma causa? | **CONFIRMADA**, SWITCH_MODEL físico |
| **H-0.9-C** | ¿612.0 de 0.2 debe originar otro GAP G5? | **RECHAZADA**, solo propagación |
| **H-0.9-D** | ¿AST hash y HEADING G5 son un solo defecto? | **RECHAZADA**, contratos distintos |
| **H-0.9-E** | ¿GAP-0.6-03 sigue vigente? | **RECHAZADA**, retirado |
| **H-0.9-F** | ¿0.7-01/02 son P1 activos? | **RECHAZADA**, candidatos |
| **H-0.9-G** | ¿CV/bench F17-BIS certifica el PDF EN→ES? | **RECHAZADA como garantía**, 0.8 FROZEN |
| **H-0.9-H** | ¿37 DQ y 22 DC exigen resoluciones independientes? | **RECHAZADA**: §16 dispone los 37 DQ y 22 DC uno a uno, incluyendo DQ-0.1-04/05 resueltas; familias causales compartidas **no** implican 59 ADR/tareas ni resuelven la evidencia física todavía diferida |

## 16. TRANSFERENCIA INDIVIDUAL DQ/DC — TERCERA PASADA

**Principio de cierre §8.2:** `RESUELTA EN ORIGEN` solo se usa cuando el HITO FROZEN declara la cuestión resuelta (DQ-0.1-04/05). `DIFERIDA` incluye subtipos **DELIMITADA**, **CONDICIONAL** o **ACOTADA**: el contrato fue estudiado, no se produjo la prueba física/decisión. **Razón común de no-bloqueo:** cada diferimiento deja cerrar la **reconciliación documental** (no pretende ejecutar ni certificar), pero **sí impide** atribuir la garantía no demostrada al PDF EN→ES o aprobar un gate que depende de esa garantía. Cada fila expresa su causa específica y destino. Los destinos hacia HITOs ya FROZEN se consideran **antecedentes**, no pruebas ejecutadas.

### 16.1 Disposición individual de los 37 DQ-IDs heredados

| DQ original | Estado forense | Evidencia faltante / razón de no resolución | Destino vinculable |
|---|---|---|---|
| DQ-0.1-01 | DIFERIDA | No se ejecutó cambio real de identidad/configuración entre generaciones | ADR Maestro (identidad) → testigo focal de replay autorizado |
| DQ-0.1-02 | DIFERIDA | No hay cuenta, credenciales, coste ni egress verificados | ADR proveedor/presupuesto → Execution Plan autorizado |
| DQ-0.1-03 | DIFERIDA | Lanzadores externos al Git/host no inspeccionados | ADR modalidad → preflight del plan según modalidad |
| DQ-0.1-04 | RESUELTA EN ORIGEN | Perímetro 0.2–0.9 asignado en §6.2 del HITO 0.1 | **Sin nueva decisión**; conservar ID y cobertura |
| DQ-0.1-05 | RESUELTA EN ORIGEN | Owner aprobó nomenclatura PPPR; **merge general #66** sigue gate futuro distinto | **Sin nueva decisión de nombre**; integración según §6.7 y owner |
| DQ-0.2-01 | DIFERIDA | Orden de lectura multicolumna no evaluado con GT físico independiente | ADR alcance/oráculos → testigo científico autorizado |
| DQ-0.2-02 | DIFERIDA | Glifos/visual y material físico requieren corpus con custodia | ADR oráculo STEM/visual → plan aprobado |
| DQ-0.2-03 | DIFERIDA | Modalidades STEM no cubiertas por prueba física autorizada | ADR criterios de cobertura → corpus autorizado/issue #34 |
| DQ-0.2-04 | DIFERIDA, DELIMITADA | Propagación perfilado→G5 auditada por código, impacto físico no medido | GAP-0.2-02 + ADR layout → testigo G5 |
| DQ-0.3-01 | DIFERIDA | Sutura trans-página real requiere documento conocido y criterio independiente | ADR evidencia de ingesta → testigo seguro |
| DQ-0.3-02 | DIFERIDA | Abreviaturas y cortes oracionales STEM no juzgados empíricamente | ADR oráculo lingüístico → plan de validación |
| DQ-0.3-03 | DIFERIDA, DELIMITADA | Consumidores G3/G5 inspeccionados; preservación física no acreditada | ADR invariantes STEM → oráculos E2E |
| DQ-0.3-04 | DIFERIDA | Aplanamiento H2/H3 observado, frecuencia y efecto físico requieren PDFs | GAP-0.3-01/GAP-0.6-02 → ADR jerarquía/testigo |
| DQ-0.4-01 | DIFERIDA | Guardias JSON/math con fake, proveedor real no autorizado | ADR proveedor → testigo focal en Execution Plan |
| DQ-0.4-02 | DIFERIDA, DELIMITADA | W06/UNKNOWN caracterizado en PPPR.0.5, eficacia real de recuperación no ensayada | GAP-0.5-01/02/03 → ADR/Execution Plan F18 |
| DQ-0.4-03 | DIFERIDA | Tokenizador, ventana y factura del backend elegido no existen aún | DC-0.4-01/03/04 → ADR presupuesto |
| DQ-0.4-04 | DIFERIDA | Modelo/proveedor comercial vigente todavía no seleccionado ni probado | DC-0.4-04 → ADR modelo/privacidad/costo |
| DQ-0.5-01 | DIFERIDA, DELIMITADA | Lease tras espera es GAP estático; impacto/timing no ensayados | GAP-0.5-02 → testigo offline focal aprobado |
| DQ-0.5-02 | DIFERIDA, ACOTADA | Crash físico/SIGKILL no probados; **power loss universal no es garantía exigida por F18** | ADR disponibilidad F18 → testigo sólo en alcance aprobado |
| DQ-0.5-03 | DIFERIDA, DELIMITADA | PPPR.0.7 verificó Compose versionado, no host realmente activo | DC-0.7-01/03/04 → gate operacional del plan |
| DQ-0.5-04 | DIFERIDA | Correlación excepción, reembolso/cobro y duplicación remota requieren proveedor | ADR observabilidad/costos F18 → plan con autorización |
| DQ-0.6-01 | DIFERIDA | No hay compilación real de UTF-8/math/imágenes ni procedencia de macros | ADR texto literal vs TeX; testigo físico autorizado |
| DQ-0.6-02 | DIFERIDA, DELIMITADA | Perfil/figura/drift necesita salida PDF y criterio visual independiente | GAP-0.2-02 + DC-0.6-03 → ADR/testigo |
| DQ-0.6-03 | DIFERIDA | No hubo SIGKILL/FS+SQLite; power loss universal no se presume | ADR F18/plan, testigo de crash sólo si aplicable |
| DQ-0.6-04 | DIFERIDA, CONDICIONAL | Ningún root con fallback completo y backing acreditado; DEGRADED no adoptado | DC-0.6-04 → ADR decide si pertenece al producto |
| DQ-0.7-01 | DIFERIDA | Proveedor/secrets/host comercial desconocidos, sin credenciales ni egress | DC-0.4-04/DC-0.7-02 → ADR/plan |
| DQ-0.7-02 | DIFERIDA, DELIMITADA | C2 contenedor sí, puente CLI host Windows→Docker no autorizado ni comprobado | DC-0.7-01 → ADR modalidad, preflight posterior |
| DQ-0.7-03 | DIFERIDA | Versiones/ACL/UID/volúmenes/SQLite del host externo no observables en Git | DC-0.7-03/04 → plan del modo aprobado |
| DQ-0.7-04 | DIFERIDA | Digest/cachés, redes y entrega real de secretos no verificados | ADR seguridad mínima → gate aislado del plan |
| DQ-0.7-05 | DIFERIDA, DELIMITADA | Workflows no cubren PR interno; testigo C2 fake histórico no prueba CI científico | DC-0.8-04 → ADR/Execution Plan de gates |
| DQ-0.8-01 | DIFERIDA, BLOQUEA CV FÍSICA | Falta materialización autorizada de 15 PDFs y verificación de custodia/hash | Owner + issue #34; plan sólo tras permiso |
| DQ-0.8-02 | DIFERIDA | Modelo EN→ES y muestras bilingües independientes sin aprobación | ADR proveedor/oráculo → evaluación autorizada |
| DQ-0.8-03 | DIFERIDA | Identidades SHA compartidas, particiones/protocolo ejecutado no acreditado | ADR independencia del benchmark, sin inferir leakage |
| DQ-0.8-04 | DIFERIDA | Matemáticas, tablas, diagramas, layout del PDF español sin prueba física | ADR invariantes/cobertura → plan de validación |
| DQ-0.8-05 | DIFERIDA | CI extrae PDF→AST, no existe gate científico del sujeto EN→ES contratado | DC-0.8-01/02/04 → ADR gate de producto |
| DQ-0.8-06 | DIFERIDA, CONDICIONAL | CLI preflight legacy no recalcula GT hash allí; caller certificante actual no acreditado | ADR sujeto/reutilización → revisión subtool sólo si gate |
| DQ-0.8-07 | DIFERIDA, CONDICIONAL | Post-run recibe provenance bool y colapsa duplicados; caller/gate no acreditado | ADR sujeto/reutilización → testigo focal sólo si gate |

**Censo:** 37 DQ-IDs **heredados de PPPR.0.1–0.8** rastreados sin reasignación; **2 RESUELTAS en origen**, **35 DIFERIDAS** total (incluidas DELIMITADA, ACOTADA o CONDICIONAL), todas con razón y destino. **No** son 35 nuevos tickets ni bloquean por sí solos el cierre de Fase 0; bloquean las afirmaciones de garantía que cada una delimita.

### 16.2 Disposición individual de los 22 DC-IDs heredados

**Regla §8.3:** los DC son cuestiones de decisión, no GAPs técnicos adicionales ni una autorización de diseño. La agrupación causal puede llevar a una misma decisión ADR; **no** requiere 22 NADR/ADR ni implementación nueva. Los fragmentos de decisión ya fijados por el owner se preservan.

| DC original | Naturaleza y estado | Destino sin decisión presupuesta |
|---|---|---|
| DC-0.3-01 | Política **PENDIENTE** sobre traducir headings o PRESERVE | ADR Maestro EN→ES |
| DC-0.3-02 | Criterio **PENDIENTE** de H1/H2/H3 y linaje de jerarquía | ADR Maestro layout/STEM |
| DC-0.3-03 | Contrato **PENDIENTE** de normalización/identidad, sin NFKC automática | ADR Maestro identidad; NADR sólo si falta norma |
| DC-0.4-01 | Presupuesto por llamada, techo/medición **PENDIENTE** | ADR Maestro proveedor/FinOps |
| DC-0.4-02 | **FIJADO** solo EN→ES; expresión verificable source/target **PENDIENTE** | ADR Maestro contrato → plan |
| DC-0.4-03 | Fallback real o rechazo fail-closed **PENDIENTE** | ADR Maestro → plan |
| DC-0.4-04 | **FIJADA** renovación de inferencia; proveedor/modelo real **PENDIENTE** | ADR Maestro backend → evaluación autorizada |
| DC-0.5-01 | Escalamiento UNKNOWN sin retry ciego **PENDIENTE** | ADR Maestro/F18 → plan |
| DC-0.5-02 | Validación de lease al comenzar efecto **PENDIENTE** | ADR Maestro/F18 → plan |
| DC-0.5-03 | Rol de sweeper, reconciliación FSM/queue/reporting **PENDIENTE** | ADR Maestro/F18 → plan |
| DC-0.6-01 | Contrato literal CODE/TABLE vs TeX legítimo **PENDIENTE** | ADR Maestro → plan |
| DC-0.6-02 | Representación visual HEADING por niveles **PENDIENTE** | ADR Maestro → plan |
| DC-0.6-03 | Perfiles/páginas/figuras y criterio de publicación **PENDIENTE** | ADR Maestro → plan |
| DC-0.6-04 | Admisión DEGRADED/fallback **CONDICIONAL, NO APROBADA** | ADR Maestro sólo si se adopta |
| DC-0.7-01 | Modalidad CLI host/contenedor/foreground **PENDIENTE** | ADR Maestro modalidad → plan |
| DC-0.7-02 | Mecanismo de secrets tras elección de proveedor **PENDIENTE** | ADR Maestro → plan |
| DC-0.7-03 | Controles imagen/red/cache/ACL mínimos **PENDIENTES** | ADR Maestro proporcional → plan |
| DC-0.7-04 | Preflight operacional no destructivo **PENDIENTE** | Execution Plan tras aprobar modalidad |
| DC-0.8-01 | Sujeto/capas de certificación **PENDIENTES** | ADR Maestro |
| DC-0.8-02 | Oráculos lingüísticos/STEM/visuales e independencia **PENDIENTES** | ADR Maestro → plan científico autorizado |
| DC-0.8-03 | Custodia y provisión de PDFs **PENDIENTES** por autorización owner | Owner / issue #34 → plan condicionado |
| DC-0.8-04 | Gates/atribución mínima/costo/aislamiento **PENDIENTES** | ADR Maestro → plan |

**Censo:** 22 DC-IDs **heredados** identificados, **0 soluciones aprobadas por este HITO**, dos con parte del alcance ya fijada en PPPR.0.4 (EN→ES y renovar inferencia). El ADR Maestro debe decidir solo lo imprescindible; el plan posterior transformará decisiones aprobadas en tareas y gates, sin crear un documento paralelo de priorización.

### 16.3 DQ-0.9-01 — pregunta **nueva de PPPR.0.9** sobre identidad de generación

**Estado:** **DIFERIDA DOCUMENTALMENTE AL ADR MAESTRO, NO RESUELTA POR PRESUNCIÓN.** `NADR-F17BIS-03` FROZEN R1/R4 exige jerarquía y contenido normalizado para su firma AST; `NADR-F17BIS-16` FROZEN R4–8 permite hashes con propósitos distintos y documentados. El código `compute_ast_hash` declara uso alternativo para comparación de parsers y excluye `heading_level/depth`, pero `prepare_contextual_plan` lo calcula en la ruta OCR y `ASTRegistry` usa `(document_id,ast_hash)` como identidad durable. **Observed:** E-0.9-025…028. **Required:** preservar identidad y linaje semánticos de la generación bajo Scope/principios; aplicabilidad normativa histórica **solo por sujeto compatible**. **Decision:** contrato exacto de identidad de generación no quedó aprobado por D-1/D-2. **Motivo de diferimiento:** requiere decisión de significado e invalidación que no corresponde a una auditoría. **No bloquea** reconciliar GAP-0.3-01/02 (se mantienen P1 OPEN sin corrección ni rebaja), **sí bloquea** decidir cómo corregirlos. **Destino:** ADR Maestro PPPR; NADR adicional solo ante vacío normativo demostrado, testigo posterior bajo plan aprobado.

### 16.4 Criterio de unicidad y destinos por familia

- **Ningún DQ/DC se declara resuelto por mera referencia a PPPR.0.7/0.8**. Esos HITOs registraron testigos y límites, no certificación real de host/PDF.
- **Ninguna fila crea obligación duplicada:** presupuesto/selección de backend, layout/perfiles, recuperación F18 y ciencia/oráculos atraviesan varias fuentes y se coordinan **por familia de decisión** en §12, sin perder sus IDs.
- **Dueño de decisión:** owner/ADR Maestro para política de producto, sujeto científico, modalidad, modelo y contrato de identidad; Execution Plan para operacionalizar únicamente decisiones aprobadas; issue #34 para corpus autorizado. No asignar propietarios de ejecución antes del plan.
- **Frontera anti-scope creep:** subtools F17-BIS, modalidad host no escogida y DEGRADED condicional permanecen observaciones/candidatos; no se prescriben mecanismos nuevos.

## 17. RECONCILIACIÓN HISTÓRICA Y NO-REGRESIÓN

- D-1/D-2 define el producto vigente. R1/R3, P6 F17-BIS, Event Log exclusivo anterior, pruebas fake y benchmark A/B son historia o herramientas delimitadas, no nuevas rutas.
- NADR-F17BIS-03 está APPROVED/FROZEN y NADR-16 admite hashes alternativos por propósito; **E-025…028 confirma** que `compute_ast_hash` alternativo también participa del linaje operativo de generación D-1/D-2. La aplicabilidad normativa final sigue **DQ-0.9-01**, sin degradar GAP-0.3-01/02 ni importar F17-BIS al producto por extensión. NADR-06 PROPOSED no revive GAP-0.6-03 retirado; NADR-09 FROZEN aplica a aislamiento G5 compatible, no a Event Log §5.1 frente a F18.
- E-0.8-026/046/047 son observaciones concretas sobre subtools históricos y no GAP productivos automáticos. Recibir booleano de provenance en núcleo puro es admisible si un caller prueba la verificación material; la biyección requiere cardinalidad/unicidad.
- Issue #34 sigue custodia autorizada de 15 PDFs. No fabricar hashes/GT, bajar threshold, inferir leakage ni equiparar HARD_FAIL topológico histórico con traducción actual. Issue #36 OPEN no prueba defecto nuevo en D-1/D-2 por título.
- Se mantienen todos los E/GAP IDs y veredictos FROZEN previos. Ninguna implementación ni suite científica se inició en este HITO.

## 21. CIERRE DEL HITO PPPR.0.9 — FROZEN v1.0.4

**Veredicto:** **FROZEN documental v1.0.4 — 2026-11-20.** El mandato de reconciliación global de Fase 0 queda **CERRADO** sobre código `main@1d21cfe`, ocho HITOs FROZEN, estados Git verificados y contratos aplicables. **14 GAP-IDs P1 heredados OPEN**, 13 núcleos causales preliminares, **30 E-0.9 P2**, ocho hipótesis terminales, 37 DQ heredadas (2 resueltas en origen, 35 diferidas con causas/destinos) **más una DQ nueva, DQ-0.9-01** (diferida al ADR Maestro); 22 DC heredados sin soluciones aprobadas. **0 GAP nuevos**, sin ejecución ni cambio productivo. No equivale a cierre de GAP ni a `PRODUCT_READINESS=PASS`.

### 21.1 Checklist de suficiencia §8.1 y campos de Gap Matrix §11.2

| Requisito | Estado y evidencia |
|---|---|
| Metadata/versión, changelog, baselines | **CUMPLE** — cabecera y v1.0.0→v1.0.4 FROZEN; `main` y rama general pinneados |
| Alcance, fuentes y 100% de los componentes del mandato | **CUMPLE** — §3/§4: ocho HITOs FROZEN reconciliados; código actual reusado a través de E-IDs, componentes externos NO VERIFICABLE; no se atribuye exhaustividad física |
| Límite epistemológico | **CUMPLE** — §2/§7: Observed ≠ Required ≠ Decision y límite por sujeto F17-BIS |
| Evidencias estables/severidad | **CUMPLE** — §10: E-0.9-001…030 P2 estables; los P1 originales siguen en sus fuentes |
| Campos de la Gap Matrix incorporada (no plantilla literal) | **CUMPLE contenido** — §14.1: 10 columnas exigidas por §11.2, 13 núcleos que conservan 14 GAP-IDs y trazan E-ID, estado, requisito, consecuencia, scope y destino ADR **pendiente**; la estructura de cinco secciones de una Gap Matrix autónoma **NO aplica literalmente** a este HITO de reconciliación |
| Estadística global y exclusiones | **CUMPLE** — §14.2: GAP OPEN/retirado/candidato, 270 E heredadas; ausencia de doble conteo |
| Hipótesis sin abiertas | **CUMPLE** — §15: H-0.9-A…H terminales, la falta de garantía externa permanece en DQ |
| DQ/DC con causa, no-bloqueo y destino | **CUMPLE** — §16: 37 DQ heredadas (2 resueltas, 35 diferidas), **1 DQ nueva DQ-0.9-01** diferida al ADR y 22 DC heredados individualizados |
| Contradicciones/autoridad/no-regresión | **CUMPLE** — §14.2/§17: 0.1↔0.4 conmutación duplicada; 0.2→0.6 perfil; 0.3 vs 0.6 heading; NADR-06 `PROPOSED`, F18 vigente |
| Resumen, veredicto, garantías y cadena Git | **CUMPLE** — §1, §21.2/21.3: resultados parciales, sin certificación, secuencia al ADR |
| Flujo de governance | **CUMPLE documentalmente** — PR #74 deberá permanecer Draft hasta revisión y aprobación separada para merge; PR #66 Draft; `main` intacto |

**Relación con §11.2:** el artefacto es un **HITO de reconciliación con Gap Matrix incorporada**, no una Gap Matrix autónoma ni una excepción que reemplace su plantilla compacta de cinco secciones. Reutiliza los **diez campos mínimos** y sus estadísticas, y mantiene las secciones forenses necesarias para trazabilidad E/GAP/DQ/DC. No se afirma conformidad literal de estructura; tampoco se crean una segunda matriz o un estándar documental nuevo.

### 21.2 Regla §8.2 — diferimientos y garantías

- **NO VERIFICABLE / diferido justificadamente:** la ejecución científica y lingüística real EN→ES, independencia de particiones, fidelidad STEM/visual física, proveedor real/costo/privacidad, host y crash, materialización/custodia de 15 PDF, así como reutilización de preflight/post-run F17-BIS. §16 identifica motivo y destino; **no bloquean cierre de auditoría read-only** porque se ha establecido qué se desconoce, pero **sí bloquean** dar las respectivas garantías o autorizar gates científicos ficticios.
- **DQ-0.9-01:** la discrepancia entre propósito declarado de `compute_ast_hash` y su uso como identidad de generación exige **decisión de semántica aplicable** en ADR Maestro; no revoca GAP-0.3-01/02 ni promulga normalización concreta.
- **POSITIVO demostrado por lectura:** D-1/D-2 selecciona una ruta única; E/GAP/decisiones están trazados sin perder sus IDs; controles de fallos y continuidad fake tienen fronteras conocidas; las limitaciones de tooling histórico, perfiles, TeX, firmas y FSM tienen propietarios documentales.
- **NEGATIVO / no acreditado:** traducción científica correcta, entrega comercial, proveedor vigente, factura/costo observado, continuidad host, CI científico end-to-end, certificación de PDF final, corrección o aceptación de ningún GAP. El conteo de GAP-IDs no demuestra incidentes reales ni defectos físicos medidos.
- **NOT_RUN:** CI, pytest, proveedores/LLM, Docker/Compose, host Windows, Tectonic, SQLite del owner, corpus/GT privados, pruebas físicas, alteración de manifest/hashes y tareas de implementación.

### 21.3 Cierre de Fase 0, siguiente gate y Git

**Fase 0 (auditoría forense) queda documentalmente completada por PPPR.0.1–0.9 FROZEN**, sujeto a integración interna autorizada del PR #74; esto **no** cierra la iniciativa PPPR ni aprueba producto, ADR o plan.

**Secuencia:** owner revisa y aprueba por separado la integración del PR interno #74 → merge solo a `pdf-pdf-product-readiness` → verificar SHA/HITO FROZEN → eliminar rama `pppr/hito-0.9` → iniciar **ADR Maestro** desde el HEAD general actualizado, sin reabrir HITOs ni crear ADR/NADR por reflejo. Luego, si es necesario, ADR de subfase / NADR compatibles y aprobados → un Execution Plan → revisión y aprobación del paquete documental del **PR #66** antes de integrar a `main` → implementación mediante PRs separados posteriores, nunca en este HITO.

**Gobernanza:** PPPR.0.9 puede estar FROZEN y **PR #74 seguir Draft**; una cosa es suficiencia documental y otra autorización de merge. Se preserva `main@1d21cfe`, PR #66 Draft y la regla de no apilar ramas cortas.
