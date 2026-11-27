# Matriz comparativa R1 — registro acumulativo vigente

**Revisión 5 · 2026-11-27 · inicialización de rúbrica 1.0.** Método: [Metodología de evaluación R1](./METODOLOGIA_EVALUACION_R1.md). Sustituye como vista vigente los cuadros históricos §§12.29–33 del [informe](./INFORME_INVESTIGACION_Y_HOJA_DE_RUTA.md), sin borrarlos ni cambiar sus observaciones. Las notas R son retrospectivas: se apoyan exclusivamente en evidencia ya documentada, no constituyen calificaciones definitivas globales. No se reejecutaron motores, ni se exigió anotar páginas. Revisión del Staff por mandato del owner; pendiente revisión del Board/aceptación de integración.

## 1. Configuraciones, conformidad y cobertura

| ID | Motor/configuración fijada | Casos completados (comunes) | Conformidad observada | Operación/admisión |
| --- | --- | --- | --- | --- |
| E0 | PyMuPDF 1.27.2.3, get_text()/get_text("dict"), sin OCR | 4/4 | FAIL_OBSERVED en TXT STEM; sin texto en S; no equivale al pipeline baseline completo | Operativo |
| E1 | MiniCPM-OCR SDK 1.0.4, llama.cpp b11901/5320c87ff CPU 6 hilos, Q8 + F16 + DSpark, ctx 8192, serial, layout/upright CPU | 4/4 | FAIL_OBSERVED STEM, gráfico, notas X y orden S; ventajas lingüísticas/tabulares | Operativo, reservas observadas respetadas |
| E2 | PaddleOCR-VL 1.6 / PaddleOCR 3.7.0 CPU | 0/4 | NOT_RUN | BLOCKED_RESOURCE_MANIFEST |
| E3 | MinerU 4.2.0 Standard ONNX/llama.cpp | 0/4 | NOT_RUN | BLOCKED_RESOURCE_MANIFEST |
| E4 | Docling 2.152.0 CPU | 0/4 | NOT_RUN | BLOCKED_RESOURCE_MANIFEST |
| E5 | pdf-inspector 1.27.1 | 0/4 | NOT_RUN | BLOCKED_RESOURCE_MANIFEST |

4/4 significa cuatro páginas comunes completadas operativamente, no cuatro aprobadas ni matriz integral de R1. Inventario R0: 21 páginas por candidato, restantes NOT_RUN (17 E0/E1; 21 E2–E5); conservar como trazabilidad sin exigir completarlas. No ampliar volumen por esta revisión. E0/E1 caracterización acotada concluida. Sin ganador; posible uso especializado sujeto a decisión R4. R2–R5 NOT_RUN.

## 2. Casos y referencias de evidencia

Abreviaturas de caso **P** E-R01 p1, **G** E-R02 p3, **T** E-R04 p2, **S** E-S03. P/G/T son digitales, S raster físicamente invertido. No confundir P de caso con nivel preparado (no ejecutado). Referencias § corresponden al informe enlazado. Identidad del PDF derivado P y hashes de las salidas en §12.28; G/T/S y ZIP revisado, hashes y resultados en §12.32; corte de palabras en §12.33. Dict local E0 no inspeccionado; N de E1 P no recibido, N de G/T/S sí inspeccionado en §12.32. No se infiere una prueba adicional del registro histórico.

| Caso | E0 tiempo s (operación; extracción) | E1 sonda s | Pico commit E0 MiB / E1 GiB | E1 RAM libre mínima GiB | Evidencia |
| --- | ---: | ---: | --- | ---: | --- |
| P | 0,24947; 0,01600 | 145,84 | NE / 4,35 | 10,34 | §§12.28/30 |
| G | 0,16138; 0,06755 | 247,12 | 58,61 / 4,76 | 10,05 | §12.32 |
| T | 0,11936; 0,01473 | 155,89 | 50,40 / 4,05 | 10,91 | §12.32 |
| S | 0,28195; 0,18644 | 52,42 | 142,75 / 4,01 | 11,00 | §12.32 |

E0 reloj antes de imports hasta extracción (incluye apertura/hash y text/dict, no escritura); E1 carga, extracción y validación. No speedup funcional equivalente. Lote E1 hasta 3,37 GiB, disco mín. 33,11 GiB en observaciones; no cuotas duras, no RSS/VRAM, ni garantía para artículo/libro. F05 no cuenta los errores de instrumentos previos como fallo del motor ni los borra: §§12.22/25–27.

## 3. Perfil comparativo por propiedad (única tabla vigente)

Cada celda acota la nota a la evidencia/caso/nivel señalado; no media entre casos. R = retrospectiva; futuras P = prospectiva. X = representación textual/exportada; N = nativa; cuando ambas se comparan, N→X. IN = INCONCLUSIVE, NE = NOT_EVALUATED, NR = NOT_RUN, B = BLOCKED (admisión), NA = NOT_APPLICABLE. Los candidatos B no reciben nota. Cuando una nota parcial positiva aparece junto a una limitación, no equivale a una nota de toda la dimensión: p. ej. A03 5R sólo para cinco reparaciones verificadas, no para conservación universal de guiones. La revisión se apoya en el informe histórico, no en una nueva inspección independiente de cada artefacto ni evaluación ciega.

| ID — propiedad | E0 | E1 | E2 | E3 | E4 | E5 |
| --- | --- | --- | --- | --- | --- | --- |
| A01 — Fidelidad textual | IN: cuerpo digital favorable, símbolos inline y ligaduras; §12.30/33 | IN: cuerpo digital favorable, no cotejo exhaustivo de notas; §12.28/32/33 | B | B | B | B |
| A02 — Completitud | IN: prosa digital observada; S texto vacío (cobertura 0R en E02); §12.32 | 0R X, G: dos notas traducibles omitidas; N las contiene, completitud N IN; §12.32 E1-OBS-04 | B | B | B | B |
| A03 — Reconstrucción de palabras | 2R X, G/T: particiones persistentes, 5 ejemplos de cuerpo; §12.33 | 5R X, G/T: 5/5 particiones de cuerpo cotejadas unidas; guiones legítimos no adjudicados; nota excluida; §12.33 | B | B | B | B |
| A04 — Reconstrucción de párrafos | 2R X, P/G/T: saltos internos sistemáticos, requiere reconstrucción; §12.28–33 | 5R X, P/G/T: párrafos de cuerpo cotejados continuos; notas no incluidas en alcance; §12.28/32/33 | B | B | B | B |
| A05 — Unicode y tipografía | IN: ligaduras y guiones físicos; raíz errónea se registra C01; §12.30/33 | IN: ligaduras normalizadas en cuerpo; signos científicos se registran C01/C02; §12.32/33 | B | B | B | B |
| A06 — Continuidad lingüística | IN: continuidad de prosa entre columnas G observada; multipágina NR; §12.32 | IN: continuidad de prosa entre columnas G observada; multipágina NR; §12.32 | B | B | B | B |
| B01 — Orden de lectura | IN: P orden de cuerpo correcto; G caption/notas desplazados, orden lógico total no adjudicado; §12.28/32 | 1R N/X, S: inversión de orden (nota primero); P/G cuerpo favorable; §12.28/32 | B | B | B | B |
| B02 — Jerarquía | 2R X, P: títulos textuales sin niveles explícitos; N dict NE; §12.29/30 | IN: P títulos ambos H1, etiquetas observadas, niveles no cotejados exhaustivamente; §12.28/32 | B | B | B | B |
| B03 — Clasificación semántica | IN: TXT sin tipos explícitos; dict de host no inspeccionado; §12.29/32 | IN: etiquetas de títulos/tabla/chart/notas observadas, fragmento ecuación como formula_number; §12.32 | B | B | B | B |
| B04 — Diseño multicolumna | IN: G prosa continúa entre columnas, geometría local no inspeccionada; §12.32 | IN: G prosa continúa entre columnas, segmentación completa no adjudicada; §12.32 | B | B | B | B |
| B05 — Notas y referencias | 2R X, G: notas recuperadas, vínculo/orden no explícito; §12.32 | 0R X, G: notas omitidas; N notas presentes pero índice material alterado (nota 5); §12.32 E1-OBS-04 | B | B | B | B |
| B06 — Asociaciones | IN: G imagen reportada y caption desplazado, vínculo no inspeccionado; §12.32 | IN: G chart/caption/fuente etiquetados, asociación física no suficientemente comprobada; §12.32 | B | B | B | B |
| C01 — Matemática inline | 0R X, P: raíz como p y relaciones linealizadas; E0-OBS-01/02 §12.30 | 0R X, P: barra K omitida; otras dos expresiones observadas conservadas; E1-OBS-01 §12.28 | B | B | B | B |
| C02 — Matemática display | 0R X, G: ecuaciones desestructuradas y símbolos perdidos; E0-OBS-03 §12.32 | 0R N/X, G/S: variables/fragmentación y x=x+1 alterada; E1-OBS-02/05 §12.32 | B | B | B | B |
| C03 — Exactitud numérica | IN: T 360 decimales coinciden con E1; cotejo independiente de todas las celdas no acreditado; §12.32 | 0R N/X, G: cifras de gráfico incompatibles con escala; T favorable 360/360 coincidencias, no certificación; E1-OBS-03 §12.32 | B | B | B | B |
| C04 — Tablas simples | NE: no adjudicación separada de tabla simple | NE: no adjudicación separada de tabla simple | B | B | B | B |
| C05 — Tablas complejas | 2R X, T: valores recuperados en líneas sin asociaciones tabulares explícitas; N dict NE; §12.32 | IN favorable N/X, T: estructura HTML 30×12, paneles y encabezados; 360/360 concordancia, celdas no verificadas independientemente; §12.32 | B | B | B | B |
| C06 — Figuras y gráficos | IN: G bloque imagen reportado, activo no inspeccionado; §12.32 | 0R N/X, G: valores incompatibles con escala en tabla generada del gráfico; activo no inspeccionado en workspace; E1-OBS-03 §12.32 | B | B | B | B |
| C07 — Código | NE: código no adjudicado | NE: código no adjudicado | B | B | B | B |
| C08 — Propiedad semántica | NE: controles de propiedad no ejecutados; no inferir de geometría | NE: controles de propiedad no ejecutados; defecto chart C06 no equivale a demostrar DF-01 | B | B | B | B |
| D01 — Procedencia | IN: página/hash de entrada confirmados, vínculo región local NE; §12.30/32 | IN: linaje de página reportado, native G/T/S inspeccionado; región completa no adjudicada; §12.28/32 | B | B | B | B |
| D02 — Geometría | NE: dict host no aportado; preliminar de otra versión no puntuado; §12.29/32 | IN: processed_image y rotación reportadas, cajas/transformación no cotejadas exhaustivamente; §12.28/32 | B | B | B | B |
| D03 — Activos visuales | IN: imagen reportada G/S, bytes/activo no inspeccionados; §12.32 | IN: activo original no inspeccionado, ausencia en N/X G no prueba pérdida irreversible; §12.32 | B | B | B | B |
| D04 — Riqueza de representación | 2R X, P/G/T: texto lineal, faltan relaciones semánticas; dict NE; §12.29–33 | IN favorable: tipos, HTML, LaTeX, notas N; relaciones completas no acreditadas; §12.32 | B | B | B | B |
| D05 — Integridad de exportación | NE: dict local no aportado para comparar N→X | 0R N→X, G: notas traducibles presentes en N, ausentes X; E1-OBS-04 §12.32 | B | B | B | B |
| D06 — Aptitud para traducción | 2R X, prosa de cuerpo P/G/T: sutura/reagrupación necesaria; ruta integral no conforme C01/C02; §12.33 | 5R X, prosa de cuerpo P/G/T (palabras/párrafos cotejados); ruta integral X 0R G por notas/STEM; §12.32/33 | B | B | B | B |
| D07 — Aptitud para reconstrucción | IN: geometría disponible por API, artefacto host no inspeccionado; PDF final NR | IN: N/X ricos, faltan activos y vínculos verificados; PDF final NR | B | B | B | B |
| E01 — PDF digital nativo | 0R X, P/G: defecto STEM demostrado en digital, prosa favorable; §12.30/32 | 0R X, P/G: defecto STEM demostrado, ventajas A03/A04/C05; §12.28/32/33 | B | B | B | B |
| E02 — PDF escaneado | 0R X, S: 0 caracteres, sin OCR; ausencia cobertura, no error operativo; §12.32 | 0R N/X, S: frases recuperadas pero fórmula alterada; §12.32 | B | B | B | B |
| E03 — PDF mixto | NR: caso mixto no ejecutado/adjudicado como tal | NR: caso mixto no ejecutado/adjudicado como tal | B | B | B | B |
| E04 — Páginas rotadas | NE: S no acredita orientación de contenido, salida vacía | 0R N/X, S: gated, orientación no corregida, orden/fórmula alterados; §12.32 | B | B | B | B |
| E05 — Densidad matemática | 0R X, G: defecto STEM en página densa; §12.32 | 0R N/X, G: variables alteradas; §12.32 | B | B | B | B |
| E06 — Abundancia tablas/gráficos | IN: T valores sin estructura X; G activo no inspeccionado; §12.32 | 0R G gráfico por falsador C06; T favorable estructura/concordancia, C05 IN; §12.32 | B | B | B | B |
| E07 — Multipágina | NR: entradas de una página | NR: entradas de una página | B | B | B | B |
| F01 — Inicialización | NE: sin reloj separado de inicialización | Dato P: servidor disponible 4,55 s; sin objetivo separado, nota NE; §12.28 | B | B | B | B |
| F02 — Extracción | Dato: 0,11936–0,28195 s de operación; sin objetivo equivalente, nota NE; §12.30/32 | 5R en cumplimiento de límite de sonda: 52,42–247,12 s, cuatro dentro de 900 s; no calificación de velocidad de producto; §12.28/32 | B | B | B | B |
| F03 — Memoria | Dato: pico commit 50,40–142,75 MiB en G/T/S; RAM mín. no consolidada aquí, nota IN; §12.32 | 5R en reserva observada: mín. 10,05 GiB; pico commit 4,76 GiB; no RSS/VRAM; §12.28/32 | B | B | B | B |
| F04 — Almacenamiento | IN: huella incremental no adjudicada de E0 | 5R en límites observados: lote máx. 3,37 GiB, disco libre mín. 33,11 GiB; §12.28/32 | B | B | B | B |
| F05 — Estabilidad | 5R: 4/4 extracciones de motor completadas, S vacío no fallo de ejecución; §12.30/32 | 5R: 4/4 extracciones de motor completadas; bloqueos anteriores del auxiliar documentados §§12.25–27; §12.28/32 | B | B | B | B |
| F06 — Independencia offline | 5R en G/T/S: ejecución del lote desconectada según checks; P sin ensayo offline; §12.32 | 5R: cuatro sondas desconectadas según comprobaciones; no certificación universal; §12.28/32 | B | B | B | B |
| F07 — Reproducibilidad | IN: versión/hash/config registrados, estabilidad por repetición NE; §12.30/32 | IN: recursos/pins/config/hash registrados, estabilidad por repetición NE; §12.28/32 | B | B | B | B |
| F08 — Integrabilidad | IN: API existente; requiere reconstrucción semántica, esfuerzo no medido; §12.29/33 | IN: SDK/servidor/layout y exportación observados; requiere resolver STEM/notas/activos, esfuerzo no medido; §12.28/32 | B | B | B | B |

## 4. Disposición y actualización

La rúbrica separa ventajas de reconstrucción de prosa (E1 A03/A04/D06) de defectos materiales STEM (E0/E1) y exportación (E1 D05); C05 favorable a E1 por estructura y concordancia 360/360, no una exactitud independiente del 100%. No se suman notas. Conservar E0/E1, sin corregir sus salidas ni repetir. Siguiente E2 sólo tras cerrar manifiesto y autorizar operación; utilizar mismos casos comunes en alcance viable, con descarte temprano conforme al método. Restantes casos NR, no fallidos. Cada nuevo resultado actualiza las columnas y, cuando sea necesario, añade observaciones focales de caso/nivel en esta matriz y referencias al informe, sin duplicar matrices en el informe. No cambios productivos ni merge; CI de destino no acreditada.
