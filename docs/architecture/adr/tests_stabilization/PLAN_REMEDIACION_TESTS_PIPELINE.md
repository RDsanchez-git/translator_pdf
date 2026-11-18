# TST-STAB — Plan de remediación de los tests del pipeline PDF→PDF

> **Estado:** ENTREGABLE TÉCNICO CERRADO Y HANDOFF ACEPTADO POR EL OWNER; integración a `main` separada del cierre de auditoría.
>
> **Período:** 2026-11-15 a 2026-11-17 (checks terminados el 2026-11-18 UTC).
> **Rama de trabajo:** `tests_stabilization`. **Carácter:** acta de campaña técnica, no ADR normativo ni certificación del producto.
> **Evidencia operativa:** [EVIDENCIA_REMEDIACIONES_TESTS.md](EVIDENCIA_REMEDIACIONES_TESTS.md).
> **Archivo completo anterior a la compactación:** [commit fijo `5e897fdbdd2b4d17d2d668f31863caa9c04fb393`](https://github.com/RDsanchez-git/translator_pdf/tree/5e897fdbdd2b4d17d2d668f31863caa9c04fb393/docs/architecture/adr/tests_stabilization/).
> **Autoridad:** cierre técnico y handoff aceptados expresamente por el owner; no autoriza por sí solo `PRODUCT_READINESS=PASS` ni modifica decisiones científicas.

## 1. Por qué se abrió la campaña

Había tests con nombres que prometían más de lo que ejecutaban, oráculos circulares, snapshots capaces de generar sus propios expected, y riesgos de escritura sobre el workspace/SQLite durante la ejecución. Un CI verde no bastaba para distinguir prueba contractual de mock, efecto real de simulación o test científico de test técnico.

**Objetivo aprobado:** que los tests de la ruta PDF→PDF detecten violaciones de contratos observables, se puedan ejecutar con seguridad proporcional y conserven trazabilidad para el futuro refinamiento. **No** rehacer arquitectura productiva, cambiar ADR/NADR FROZEN, producir nuevos Ground Truth, regenerar corpus, rebajar umbrales científicos o afirmar E2E físico.

## 2. Método y rigor proporcional

La unidad de auditoría fue el **test o parametrización material agrupada por contrato/SUT**; no un expediente por cada nodeid ni una mutación por cada fake. La secuencia fue: inventario A → remediación focal B → controles negativos C → CI técnico real → dictamen/handoff.

| Etiqueta | Significado exacto | Decisión práctica |
|---|---|---|
| **CERRADO DOCUMENTAL / FOCAL** | Se hizo y revisó el entregable específico (inventario, corrección, falsador o CI). | No volver a auditarlo salvo nueva falsa garantía o contrato material alterado. |
| **CONFIABLE_PARA_SU_ALCANCE** | Testigo con SUT, oráculo y evidencia causal pertinente para **ese** subcontrato. | No extrapolar a otros campos, procesos ni al E2E científico. |
| **LIMITADO** | Test válido de componente, mock o contrato parcial, con frontera bien identificada. | Se conserva; no equivale a error, deuda automática o riesgo P0 nuevo. |
| **NOT_RUN** | No se ejecutó una falsación determinada; puede existir PASS del test. | No atribuir `KILLED`; decidir una falsación focal solo ante obligación contractual concreta. |
| **DEFECTUOSO** | Oráculo falso/tautológico, cobertura proclamada sin SUT, mutante que sobrevive donde debía morir. | Remediar o reclasificar, sin ajustar expected para recuperar verde. |
| **ABIERTO** | Falta una condición literal, un control físico o autorización. | Explicar qué evidencia/decisión falta; no pedir perfección por rutina. |

**Regla:** PASS no es KILLED; un SKIP no es PASS; Git limpio no es aislamiento OS; trabajo técnico terminado no es readiness de producto.

## 3. Alcance de la auditoría A — decisión final

| Hito | Resultado aceptado | Límite |
|---|---|---|
| **A-00** | Alcance, baseline y archivos protegidos fijados. | No certifica ejecución. |
| **A-01** | Inventario reconciliado: **1.476 nodeids históricos / 173 archivos**; colección posterior en CI #293 **1.478 ítems**. | Agrupación por contrato; no 1.478 oráculos acreditados. |
| **A-02** | **Ocho fronteras prioritarias** con SUT, testigo, oráculo y efectos prohibidos identificados. | El mismo falsador no acredita toda la frontera. |
| **A-03** | Oráculos/mocks examinados y falsas garantías corregidas; excepciones nombradas. | Sensibilidad no universal. |
| **A-04** | **35 fichas TR**: **7 confiables para subcontratos focales, 28 LIMITADO**; **36 archivos/165 nodeids** compartidos clasificados sin fichas redundantes. | Clasificación semántica ≠ 35 ni 165 pruebas científicas. |
| **A-05** | Mitigaciones de red/fixtures y **criterio operacional proporcional de runner hospedado** aceptado por owner. | **P4/P6 físicos abiertos**: no hay atestación OS de cero egress o I/O transitorio. |
| **A-06** | Baseline **CI técnico #293 SUCCESS** para el merge sintético del PR #63. | Baseline por SHA, no todos los HEAD futuros ni certificado de seguridad OS. |
| **A-07** | Matriz de brechas P0/P1/P2, límites y prioridades aceptada documentalmente. | No todos los límites son defectos. |

## 4. Reparaciones B — lo que se cambió

| Hito | Decisión final de alcance |
|---|---|
| **B-01/B-02** | Sustitución de falso golden de parser y snapshot autoescribible de chunker por oráculos técnicos verificables; falsadores K focales. |
| **B-03/B-04** | Nombres y afirmaciones E2E/fidelidad/healing ajustados al SUT real. El consumidor FinOps es mockeado, no PDF→PDF físico. |
| **B-05** | Riesgos concretos de rutas, SQLite, CWD, caché y opt-in de proveedor real mitigados en tests. **B-05 global abierto** por P4/P6 físico. |
| **B-06** | Revisión contractual de testigos G3/G5 y fronteras prioritarias. |
| **B-07/B-08/B-09** | Diff revisado, CI técnico del candidato ejecutado y excepciones con aceptación expresa del owner; **cerrados como entregables de revisión**, no como garantía universal o permiso de merge. |

**El resultado conservado en el árbol de integración son los mismos 21 archivos bajo `tests/` revisados y ejecutados.** La documentación y scripts de investigación fueron condensados/retirados del árbol, sin tocar tests ni producción. La correspondencia individual y las razones están en [la evidencia técnica](EVIDENCIA_REMEDIACIONES_TESTS.md).

## 5. Controles negativos C — qué detectan

**15 controles históricos reportados `MUTATION_KILLED`**, con causa contractual y SHA propio: B-05 (2), B-01/B-02 (2), G3/G5 (3), A-03 (2), foreground (2), CLI (2), G5 worker (2). No se duplican por frontera ni se heredan entre SHAs.

| Estado | Alcance aceptado |
|---|---|
| **C-00, C-09** | Diseño y publicación de matriz de 8/8 fronteras, con E/K/NOT_RUN y exclusiones. |
| **C-01, C-03, C-04, C-05** | Falsación focal acreditada: extracción, efecto incierto G3, proyección G3 y lease G5. |
| **C-02** | Rechazos de bindings W08/G3-B3 y no-escritura observable; **sin K de extremo a extremo** del plan completo. |
| **C-06** | Falsadores de CLI, foreground y G5 acotados; no pipeline OCR→PDF físico. |
| **C-07** | Sensibilidad focal acreditada; `MF-B3-03 K=NOT_RUN` y dimensiones adicionales de identidad/receipts/epochs no acreditadas universalmente. |
| **C-08** | Ejecución operacional proporcional; **hermeticidad física global no demostrada**. |

**Excepción específica:** G3-B3 B3-08 exige `DUPLICATE_MEMBER`, pero la falsación particular `MF-B3-03` es `NOT_RUN`. Se conserva el test como **LIMITADO** y no se añade una mutación por obligación burocrática. Cualquier nueva falsación se condiciona a un riesgo P0 demostrable.

## 6. Evidencia de validación real y ciencia separada

| Fuente | Evidencia | Interpretación |
|---|---|---|
| [PR #63 — cerrado sin merge](https://github.com/RDsanchez-git/translator_pdf/pull/63) | HEAD aportado `428330317edcbc584ef834d3e81946c9ef361926`; **merge probado `0798f7f99663b79123e225132fea1385df9f285a`**. | Su CI no acredita commits posteriores puramente documentales ni candidatos futuros distintos. |
| [CI técnico #293](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44207210090) | Static (Pyright/import-linter) SUCCESS; unit **225 PASS**; integración marker **72 PASS**; cinco pasos explícitos **138 ejecuciones con solapamientos**; `not e2e` **1.454 PASS, 4 SKIP, 20 deselected**, tres warnings. | Evidencia suficiente de estabilidad técnica del merge evaluado; los 4 SKIP **no** son PASS. |
| [CV científico #47](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44207209078) | **FAILURE** de preflight `BASELINE_INTEGRITY_FAILURE` exit 3: faltan 15 PDFs `doc_08..doc_22`. Checks de no-mutación de oráculos y corpus SUCCESS; FULL SKIPPED. | Bloqueo preexistente de D-5, sin métricas científicas; no modificar GT/corpus/umbrales para obtener verde. |
| [CI anterior #292](https://github.com/RDsanchez-git/translator_pdf/actions/runs/44005819069) | SUCCESS técnico sobre PR #62 cerrado. | Corroboración histórica independiente; no sustituye CI del candidato #63. |

## 7. Riesgos residuales aceptados y handoff

| Dominio | Qué protege hoy el alcance técnico | Qué se deja expresamente fuera / responsable por rol |
|---|---|---|
| **B02 / AST / W08** | Texto literal de PDF temporal, conservación de miembros/bytes, identidades, rechazo de planes inconsistentes y sin escrituras en escenarios puntuales. | `MF-B3-03` NOT_RUN, toda sensibilidad W08, OCR/ciencia, cache/replay completo. **Owner/maintainer de ruta**; [issue #36](https://github.com/RDsanchez-git/translator_pdf/issues/36). |
| **G3** | UNKNOWN no reintenta fake, publicación/proyección con rechazo de drift, FSM y SQLite durables. | HTTP exactamente-una-vez real, todas las variantes CAS/receipts, atomicidad multihost. **Owner/maintainer G3**. |
| **G5 y CLI** | Lease viejo no publica PDF, fallo persistido, CLI no hace fallback inseguro ni éxito falso. | Tectonic/OCR/provider físico, compilación científica multihost. **Owner/maintainer G5/CLI**. |
| **A05 / C08 seguridad** | Runner GitHub hospedado descartable, opt-in Groq real SKIP, permisos por defecto de token read-only confirmados por owner, archivos protegidos sin cambios persistentes en focales. | Cero egress OS, I/O transitorio/externo, secretos administrativos no auditables. **Owner/maintainer CI** valida entorno del PR de integración. |
| **D-4 / D-5 posteriores** | Transferencia de los testigos y sus límites al refactor. | Evaluación integral PDF→PDF y ciencia; corpus canónico/licencias/GT según [issue #34](https://github.com/RDsanchez-git/translator_pdf/issues/34). **Owner del roadmap**. |

Los **17 scripts auxiliares** y expedientes intermedios no son dependencias del CI ni productos permanentes; siguen disponibles en el [commit histórico congelado](https://github.com/RDsanchez-git/translator_pdf/tree/5e897fdbdd2b4d17d2d668f31863caa9c04fb393/docs/architecture/adr/tests_stabilization/). La reducción de archivos **no borra la historia Git** ni convierte scripts descartados en evidencia reproducida hoy.

## 8. Acta formal y estado del gate de integración

**Aprobación explícita del owner, 2026-11-17:** cerrado el **entregable técnico de TST-STAB y aceptado el handoff** con limitaciones proporcionales. No se aprueba por ese acto `PRODUCT_READINESS=PASS`, seguridad absoluta, calidad científica ni E2E integral.

**Criterios §13 de la campaña:** cinco de ocho satisfechos **en su alcance**: protecciones y negativos acotados; falsas garantías corregidas; CI real sobre el merge probado; handoff; diferimiento D-4/D-5. Tres eran **condiciones globales** pendientes al firmar el acta: gates A/B/C completos, hermeticidad física y autorización de integración. Estos límites no se ocultan por cerrar el entregable.

**Decisión de consolidación documental posterior:** reducir la carpeta a **este plan y `EVIDENCIA_REMEDIACIONES_TESTS.md`**; los 21 tests quedan intactos. Para integrar se requiere PR de `tests_stabilization` a `main`, checks sobre su merge SHA, revisión y decisión de merge. **Registrar el estado real de esa integración mediante su PR**, no suponerla ocurrida por esta acta.

**Criterio permanente:** no corregir tests para que el CI quede verde sin identificar causa contractual. Conservar las protecciones que detectan daños reales, y no transformar fakes honestos, `LIMITADO` o `NOT_RUN` en deuda artificial.

## 9. Fuentes de trazabilidad

- [Evidencia técnica condensada](EVIDENCIA_REMEDIACIONES_TESTS.md): 21 archivos, correcciones, controles K y baseline.
- [Expediente completo previo a la reducción — SHA fijo](https://github.com/RDsanchez-git/translator_pdf/tree/5e897fdbdd2b4d17d2d668f31863caa9c04fb393/docs/architecture/adr/tests_stabilization/): fuentes originales A-00/A-07, matrices A-01/A-04, A-05, scripts de auditoría, informes de falsación y cronología. **Consultar con ese SHA**, no con rutas eliminadas de `main`.
- [PR #62](https://github.com/RDsanchez-git/translator_pdf/pull/62) y [PR #63](https://github.com/RDsanchez-git/translator_pdf/pull/63), cerrados sin merge: historial verificable de CI y CV.
