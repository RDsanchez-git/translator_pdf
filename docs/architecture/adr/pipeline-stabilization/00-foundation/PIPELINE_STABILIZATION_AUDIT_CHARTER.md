# PIPELINE_STABILIZATION_AUDIT_CHARTER.md
## Charter de preregistro: Estabilización y Reconciliación Arquitectónica del Repositorio

* **Versión:** 0.1.0
* **Estado:** DRAFT (pendiente de aprobación del Architecture Board)
* **Fecha de emisión:** 2026-10-14
* **Autoridad:** Architecture Board
* **Identificador de unidad:** {por asignar por el Board; de él derivan los IDs E-{U}.{H}-NNN, GAP-{U}-NN, H-{U}-NN}
* **Ubicación propuesta:** {por decidir por el Board}
* **Precedente de forma:** FASE0_AUDIT_CHARTER (F18)
* **Naturaleza:** plan de auditoría y preregistro de criterios. NO es HITO ni evidencia forense. NO es un documento de meta-gobernanza (§9.3 de la metodología general).
* **Base de código congelada:** commit 95ef8a38 (rama fase18_subfase02_gate01, 2026-10-13); main = 6b740e0a. Tag inmutable en GitHub: {pendiente}.
* **Origen autoritativo:** GitHub (RDsanchez-git/translator_pdf). GitLab es mirror con sobrescritura de ramas divergentes.

### Changelog
| Versión | Fecha | Cambio |
|---|---|---|
| 0.1.0 | 2026-10-14 | Esqueleto inicial. Sin evidencias consolidadas. |

---

## 1. NATURALEZA Y LÍMITES

1.1 Este Charter fija, ANTES de medir, qué se audita, con qué criterios y qué cuenta como saneamiento. Evita criterios posteriores al resultado.
1.2 Vocabulario de evidencia usado en este borrador:
* DEMOSTRADA: resultado de ejecución corrida por el owner.
* VERIFICADA: lectura estática de código o documento citada.
* INFERIDA: conclusión razonada, sin ejecución ni cita directa.
* SIN VERIFICAR: afirmación recibida y no comprobada.
Los HITOs posteriores cierran hipótesis con CONFIRMADA / RESUELTA / RECHAZADA / NO VERIFICABLE (1.2_METH §10). Cambiar ese vocabulario requiere al Board (§14.2).
1.3 La auditoría es read-only sobre código funcional, NADRs/ADRs FROZEN y main. La ejecución dinámica la corre el owner (Windows, PowerShell, venv). No se pegan claves.
1.4 Esta unidad está FUERA de F18. F18.2 queda congelada en Gate 1 / Wave 1.1.
1.5 Objetivo: cambios reales y verificables en el pipeline, no solo un informe de defectos.

## 2. AUTORIDAD DOCUMENTAL

2.1 Estado observado de la metodología general:
* Archivo `1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md`: v1.3.0 FROZEN. Cabecera "Última actualización 2026-08-25". La fila 1.3.0 del changelog conserva el placeholder `{fecha actual}`. No existe fila 1.4.0. [VERIFICADA]
* Citan v1.4.0: `2_METH_ADR_MASTER` v1.0.1 (derivación) y `FASE0_AUDIT_CHARTER` F18, ambos FROZEN. [VERIFICADA]
* Citan v1.3.0: planes 17-BIS (Fase 3, Fase 5), plan F18.1, HITO_18.2.0. [VERIFICADA]
* MR !4 (merged 2026-10-01) anuncia "changelog v1.4.0, fila en §3.1, nota en §6.1 paso 2, nota de nomenclatura". El commit 1e287b61 modifica un solo archivo: `2_METH_ADR_MASTER.md` (+247). [VERIFICADA]
* Ningún commit del historial del archivo de metodología (cc53438f, ea703f62, b74bf480, 7689a56c) contiene la 1.4.0; `git log --all -S"1.4.0"` sin resultados. [DEMOSTRADA]
* 7689a56c (2026-10-08) dice "actualizar metodología v1.3.0" una semana después de las citas a 1.4.0 y no completa la cabecera. [VERIFICADA]. Hipótesis de origen (1.4.0 redactada localmente y no commiteada): [INFERIDA].
2.2 Rutas colgantes: la cabecera declara `docs/architecture/METHODOLOGY_...` y el archivo es `1_METHODOLOGY_...`; HITO_18.2.0 cita `METHODOLOGY_FOR_FORENSIC_HITOs.md` y el archivo es `1.2_METH_FOR_FORENSIC_HITOs.md`. [VERIFICADA]
2.3 Autoridad para elevar esta unidad: `2_METH_ADR_MASTER` §2 permite al Board elevar una sub-fase a unidad con re-baseline propio (precedente 17-BIS) y exige auditoría forense con HITOs en 00-foundation antes del ADR Maestro. Esta unidad no es una fase del ROADMAP: aplicar §2 es una INTERPRETACIÓN del Board que debe quedar registrada. [VERIFICADA el texto; la interpretación es decisión]
2.4 NADR-F17BIS-11 (raíz de composición única) figura en Ciclo de Vida DRAFT. NADR-F17BIS-08 está FROZEN pero no contiene regla de unificación CLI/daemon. NADR-F18-01 a 05 figuran FROZEN. [VERIFICADA]

## 3. DECISIONES DEL BOARD (propuestas, pendientes de aprobación del owner)

D-1 Principio de ejecución canónica. Un solo camino canónico PDF -> PDF; la CLI es adaptador de entrada, no segundo traductor; benchmark y mocks separados de producción. Canónico es un CONTRATO de ejecución (contexto, validación, healing, journal, cola/FSM), no un archivo.
D-2 Objetivo de convergencia. El objetivo es el plano de ejecución persistente con las garantías de F18. Qué código lo materializa NO se decide hoy: se decide con la evidencia del E2E-0 (§6.1). Inclinación provisional, no vinculante: núcleo de procesamiento de `pipeline_factory`/`AsyncDispatcher` con cola y FSM como capa de planificación.
D-3 Caracterización antes de remediar. Se ejecuta E2E-0 sobre cada ruta existente, con criterios preregistrados abajo.
D-4 F18.2. Tag en GitHub sobre 95ef8a38 y pausa. Sin documento de checkpoint. Los registros cerrados no se reescriben; se reabren por la fila de revisiones tardías del Register. Wave 1.1 no se declara fallida: su garantía se demostró sobre código que hoy no se despliega.
D-5 Metodología. Sin §6.8 ni documento nuevo (§9.3). Emitir 1.4.0 por el cauce del Board: (a) fecha del changelog 1.3.0; (b) cumplir lo anunciado en !4; (c) cláusula de evidencia de integración en §6.4 (§6.2 de este Charter la fundamenta); (d) reconciliar rutas colgantes. El changelog registra que 1.4.0 fue anunciada en !4 / 1e287b61 y no llegó al archivo. No se editan los FROZEN que ya la citan. Alternativa no elegida: numerar 1.5.0.
D-6 Instrumentos primero (Batch 0): configuración de Pyright, alcance de CI, build de Docker, credenciales de proveedor (§8).
D-7 Evidencia de 17-BIS: no es estado actual. Cada hallazgo heredado se re-verifica contra el código antes de reutilizarse. P7-R02 (absorber engine.py en el orquestador de la CLI) queda superseded por D-2. GAP-P4-02 se reabre como hallazgo de esta unidad.

## 4. ALCANCE Y EXCLUSIONES

4.1 En alcance:
* Rutas de ejecución: `runtime/engine.py`, `apps/cli/main.py` + `pipeline_factory`, `apps/llm_workers/__main__.py`, `apps/ocr_router`, `apps/compiler`, `apps/daemons/reconciler.py`, `runtime/sweeper.py`.
* Instrumentos de verificación: configuración Pyright, `.github/workflows/ci.yml`, markers de pytest, `Dockerfile`, `docker-compose*.yml`, dependencias.
* Contratos de identidad, persistencia entre procesos, ensamblado, preservación científica de nodos.
4.2 Fuera de alcance:
* Umbrales de calidad científica (NSS, thresholds de regresión), re-baseline del corpus v4.0 (proceso de 17-BIS), modificación de oráculos sellados (NADR-26).
* Funcionalidad de Fases 19 a 21 e infraestructura distribuida.
* Nueva implementación de F18.2 (no se abre Wave 1.2).
* Modificación de ADR/NADR FROZEN y de main.
4.3 Los benchmarks y runners son instrumentos de medición, no sujetos de remediación, salvo contaminación de la ruta productiva.

## 5. HIPÓTESIS PREREGISTRADAS

| ID | Enunciado | Estado actual | Base |
|---|---|---|---|
| H-01 | `LLMWorkerDaemon` llama a métodos que `ControlPlaneRepository` no define (`claim_next_pending_task`, `mark_task_failed`) | DEMOSTRADA | `hasattr` False; `git grep` solo encuentra las llamadas; `git log -S` sin resultados (historia completa) |
| H-02 | Pyright "strict" de pyproject.toml no se aplica al invocar `pyright` sin `-p`, por precedencia de `pyrightconfig.json` | DEMOSTRADA (local) | 0 errores sin `-p`; 105 con `-p pyproject.toml` |
| H-02b | El CI sufre lo mismo | INFERIDA | `ci.yml` ejecuta `pyright core/ apps/ infra/ runtime/` sin `-p` |
| H-03 | El CI ejecuta como máximo 191 de 1014 tests (149 `unit`, 42 `integration and not regression`); 823 sin esos markers; 0 con marker `regression` | DEMOSTRADA | `pytest --collect-only` |
| H-04 | La ruta desplegada es `runtime/engine.py`; el daemon no lo lanza ningún artefacto del repo | VERIFICADA | compose, Dockerfile CMD, `git grep` |
| H-05 | La dualidad CLI/engine fue registrada en 17-BIS (P7-H01, GAP-P4-02), no tiene regla en NADR-08/11 y no figura en el consolidado de 17-BIS | VERIFICADA | lectura de HITO, Gap Matrix, NADR-08, consolidado |
| H-06 | La composición está duplicada en al menos tres entry points | VERIFICADA | lectura de cli/main, engine, llm_workers/__main__ |
| H-07 | El compose base activa `IS_BENCHMARK=1`; `engine.py` tiene rama de benchmark también por prefijo `doc_` | VERIFICADA | lectura; el golden lo fija en 0 |
| H-08 | Ningún compose inyecta `GROQ_API_KEY`; el golden pasa `GEMINI_API_KEY` y el código exige la primera | VERIFICADA (grep); efecto INFERIDO | `git grep`, lectura |
| H-09 | `requirements.txt` no existe y el Dockerfile lo copia; `docker build` fallaría | Ausencia DEMOSTRADA; fallo INFERIDO | `git ls-files`, `Test-Path` |
| H-10 | toxiproxy/fake-gemini no intercepta tráfico (ningún `.py` de producción lee `GEMINI_API_URL`) | DEMOSTRADA por grep | `git grep` |
| H-11 | `classify_external_effect`, `TaskLeaseHeartbeat` y `mark_task_completed` no tienen consumidor en la ruta desplegada | VERIFICADA | `git grep` |
| H-12 | La evidencia "dinámica" de F18.1 Task 4.2.1 no ejercita el daemon | VERIFICADA el texto; causalidad INFERIDA | plan F18.1 |
| H-13 | F18.1 introdujo `abandon_execution(task_id, reason=...)` con firma incorrecta, corregida en 95ef8a38, y cerró con tests y Pyright en verde | VERIFICADA | diff 86e8e43, mensaje 95ef8a38 |
| H-14 | `apps/compiler/__main__.py` usa `InMemoryProfileStore`; con procesos separados fallaría la lectura del perfil | Uso VERIFICADO; efecto SIN VERIFICAR | búsqueda de código |
| H-15 | `runtime/reconciliation.py` fue eliminado en 17-BIS (DF-25); P7-H02/GAP-P7-03 cerrados por eliminación | VERIFICADA | Register F1; `Test-Path` False |
| H-16 | El informe de 17-BIS sobre "compiler eludiendo CompilationService" está desactualizado | VERIFICADA | `apps/compiler/__main__.py` lo construye |
| H-17 | `engine.py` invoca el procesador también para nodos PRESERVE; si eso llega al LLM es SIN VERIFICAR | SIN VERIFICAR | lectura parcial |
| H-18 | El bug "unknown_ast_hash" (P7-H06) sigue presente | RECHAZADA (resuelta) | core/execution/handlers.py usa cmd.ast_hash; la cadena solo figura en un comentario que cita NADR-08 §5.3 R8-R10. Cobertura de tests: SIN VERIFICAR |
| H-19 | Los PDFs doc_08 a doc_22 no están disponibles en CI; ci.yml no los materializa | Hallazgo previo VERIFICADO (HITO_6.2, FROZEN); vigencia del gap SIN VERIFICAR | .gitignore excluye tests/corpus/canonical/pdf/; ci.yml sin paso de provisión; cuántos PDFs están versionados hoy: SIN VERIFICAR |
| H-20 | Causa raíz de la brecha: el DoD (§6.4) no exige evidencia sobre la ruta desplegada y los gates midieron lo unitario y estático | INFERIDA | hallazgo del DoD: VERIFICADO; causalidad: hipótesis |
| H-21 | Existe un segundo workflow (continuous-verification.yml, perfil FULL, push a main) con la misma dependencia de PDFs | VERIFICADA | lectura del workflow |
| H-22 | El job regression-gates condiciona integration-tests (needs); su fallo por corpus incompleto impediría ejecutar integración | INFERIDA | ci.yml |


## 6. CRITERIOS DE ACEPTACIÓN PREREGISTRADOS

6.1 E2E-0 (caracterización, no remediación). Para CADA ruta de §4.1 con entrada de documento:
* Entrada candidata: uno de los PDFs doc_01 a doc_07 de tests/corpus/canonical/pdf/ (versionados, con sha256 en manifest.json). Selección por tamaño y contenido: {por designar por el Board}.
* Proveedor: determinista y controlado, con respuestas conocidas.
* Resultado por ruta, clasificado SOLO como: (A) PDF final válido; (B) producto parcial, con etapa de fallo identificada; (C) fallo, con causa y traza.
* Decisión de convergencia (D-2): si solo una ruta alcanza (A) esa es la base; si ambas, se elige por riesgo y complejidad con evidencia; si ninguna, el primer batch es el defecto de integración.
6.2 Matriz de aceptación del saneamiento (aplicable a la ruta canónica elegida):
| Dimensión | Criterio |
|---|---|
| Entrada | PDF versionado con hash verificable |
| Ruta | Raíz de composición identificada; sin atajos de benchmark ni mocks |
| Proveedor controlado | Flujo completo con respuestas conocidas |
| Proveedor real | Inferencia efectiva con presupuesto autorizado: {monto por fijar} |
| Identidad | Trazabilidad coherente documento, AST, chunk, nodo, tarea, intento |
| Persistencia | Resultados recuperables desde una conexión o proceso nuevo, según contrato |
| Preservación | Fórmulas, código e imágenes (PRESERVE) intactos |
| Ensamblado | PDF final válido derivado de resultados materializados |
| Estado operativo | Estado final coherente con evidencia de la ruta ejecutada |
| Reproducibilidad | Commit, entorno, configuración y comandos registrados |
6.3 Separación: defectos de conectividad del pipeline no se mezclan con defectos de calidad científica. No se fijan umbrales numéricos de calidad, latencia o costo en este Charter.
6.4 Precondiciones (Batch 0): clave de proveedor coherente con el código; `tectonic` en PATH o Docker operativo; Pyright medido con `strict`; alcance de CI documentado. Un E2E con mocks no sustituye al real; la ausencia de duplicación observable no prueba su ausencia.
* El corpus de PDFs usado por regresión debe estar disponible en CI (versionado o materializado por un mecanismo documentado), o el CI debe declarar qué subconjunto verifica.
6.5 Clasificación de apoyo: todo E2E se ejecuta sobre la ruta que el compose despliega o sobre la que el Board declare canónica, nunca sobre una ruta no ejecutable.

## 7. MÉTODO DE AUDITORÍA DELTA

7.1 Punto de partida obligatorio (1.2_METH §9.4): 17-BIS (HITOs 0.x a 6.x, Gap Matrix de 40 GAPs, consolidado de 15 pendientes), F18 (HITO 0.1 a 0.12 con 25 GAPs; HITO 18.2.0 a 18.2.2), registros de F18.1 y F18.2.
7.2 Tratamiento de cada hallazgo previo:
| Categoría | Tratamiento |
|---|---|
| Confirmado y vigente | Referenciar, sin duplicar |
| Resuelto | Verificar evidencia contra el código actual y conservar |
| Parcialmente resuelto | Registrar delta exacto |
| No demostrado | Diseñar prueba de confirmación o refutación |
| Nuevo | Evidencia e ID conforme a la unidad |
7.3 Clasificación obligatoria en tres vías de cada hallazgo:
* Vía A: violación de contrato vigente (corrección bajo el NADR existente, sin decisión nueva).
* Vía B: vacío normativo (decisión y, si procede, NADR nuevo).
* Vía C: contradicción entre contratos (resolver autoridad antes de tocar código).
Clasificación provisional, sujeta a lectura de NADR-F18-01, 02, 04, 05 y los 25 GAPs: dualidad de rutas (H-05, H-06): vía B, o A si NADR-F17BIS-11 se congela; DoD (H-20): vía B; H-01: A o C según el contrato que se declare canónico.
7.4 Los hallazgos con causa común se agrupan por problema estructural, no por archivo. Se separan bugs locales de decisiones de consolidación.
7.5 Reapertura de hallazgos RESOLVED (p. ej. DF-18.2-01, 02, 04): por la fila de revisiones tardías del Register, sin tocar el Evidence Log (inmutable, §3.5.2). La existencia y el formato de esa fila fueron indicados por el owner y no los verifiqué.
7.6 Identificadores: E-{U}.{H}-NNN, GAP-{U}-NN, OBS-{U}-NN, H-{U}-NN; severidad solo P0 a P2; Observed / Required / Decision separados. El ADR Maestro y los NADR se emiten solo donde la clasificación lo exija (§6.1, §8.2 de la metodología).

## 8. BATCHES PREVISTOS (orden, no diseño)

* Batch 0, instrumentos: unificar la configuración de Pyright (línea base: 105 errores bajo strict; el CI debe usar la misma configuración); documentar y ampliar el alcance de CI; resolver Dockerfile/dependencias; alinear credenciales; resolver el estado de los NADR en DRAFT que respaldan tareas.
* Batch 1: E2E-0 y decisión de convergencia (§6.1).
* Batches 2 a n: definidos por la matriz de hallazgos y su clasificación; cada batch con criterio de cierre por E2E y rollback.
* Cierre: E2E determinista y E2E con proveedor real sobre la ruta canónica.
Ningún batch se ejecuta sin respaldo normativo (NADR FROZEN o decisión aprobada).

## 9. CONDICIONES DE REANUDACIÓN DE F18.2

* Se reanuda cuando exista la ruta canónica verificada por E2E y se evalúe lo ya implementado: compatibilidad total, parcial o incompatibilidad demostrada (en cuyo caso, remediación específica y actualización del plan).
* No se reescriben los completion logs. La pausa se registra como decisión de control de ejecución referenciada desde el estado operativo existente, sin crear un estado nuevo en el Execution Plan.
* Se re-evalúan las garantías de autoridad y fencing sobre la ruta canónica, no sobre el daemon actual.

## 10. PENDIENTE DEL BOARD

1. Identificador y ubicación de la unidad.
2. Aprobar D-1 a D-7, o ajustarlas.
3. Interpretación de `2_METH_ADR_MASTER` §2 para esta unidad.
4. Versión: 1.4.0 (propuesta) o 1.5.0, y su contenido.
5. PDF de E2E-0 y presupuesto del E2E real.
6. Estado (DRAFT o FROZEN) de NADR-F17BIS-11 y su relación con esta unidad.
7. Tag en GitHub sobre 95ef8a38.

## 11. LO QUE ESTE CHARTER NO AFIRMA

* No afirma que el daemon, `engine.py` o la CLI sea la ruta correcta.
* No afirma causalidad entre el DoD y los defectos (H-20 es hipótesis).
* No afirma que `docker build` falle ni que el E2E real fallará por configuración: son inferencias.
* No se han leído: NADR-F18-01, 02, 04, 05 (más allá del encabezado), los 25 GAPs de F18, el cuerpo del Execution Plan de F18.2, ENGINEERING_PRINCIPLES, HITOs 0.4.5 P1 a P6. HITO_6.2 (leído parcialmente, líneas 215 a 274).
* No hay ejecución de chaos ni E2E hasta aprobar este Charter.
