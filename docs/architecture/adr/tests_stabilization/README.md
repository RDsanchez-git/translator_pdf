# Tests Stabilization — Guía de entrada

**Estado:** EN EJECUCIÓN. **A-00 completado**, **A-01 parcialmente documentado, todavía abierto**, A-02…A-07/B/C pendientes. **Sin remediaciones de código ni pruebas dinámicas ejecutadas por esta campaña**.

**Rama de trabajo:** `tests_stabilization` (desde `main` @ `83ef0257f795f0d973f9393cc225e7af5b956ade`).

## Empezar aquí

Leer el **[Plan de estabilización y remediación de los tests PDF→PDF](PLAN_REMEDIACION_TESTS_PIPELINE.md)**: es el documento rector operativo de esta carpeta. Sus tareas se registran con casillas y evidencias (SHA, PR, test y mutación).

**Secuencia autorizada:**
1. **A — Auditoría semántica de tests:** contratos, SUT real, mocks, oráculos y cobertura efectiva de CI.
2. **B — Remediación de falsas garantías:** eliminar tautologías y aprobaciones automáticas, y corregir pruebas que dicen cubrir más de lo que ejercitan.
3. **C — Controles negativos y sensibilidad:** demostrar que los tests **fallan ante una violación controlada**.

**Diferidos hasta después del refinamiento del pipeline:** consolidación/ejecución integral de la ruta PDF→PDF (**D-4**) y evaluación científica, corpus canónico/GT, re-baseline y CV (**D-5**). Se documentan, pero **no forman parte del trabajo activo**.

## Evidencia de avance

- **[A-00 — Línea base, inventario y riesgos](A00_BASELINE_INVENTARIO_Y_RIESGOS.md)** — completado por lectura de código y árbol Git: 177 módulos `test_*.py` en 188 archivos Python bajo `tests/`, selección CI y superficies peligrosas de I/O. No contiene resultados de ejecución de pytest; **no acredita cobertura ni capacidad falsadora**.
- **[A-01 — Índice consolidado, 16 anexos](A01_INVENTARIO_CONSOLIDADO_Y_GATES.md)** — **EN CURSO**: 177 módulos y 1.474 nodos recolectados. **A01-S6 cerrado**: [24/24 diferencias y 133 expansiones explicadas](A01_RECONCILIACION_EXHAUSTIVA_PARAMETRIZACIONES.md). **A01-S5 en curso:** [19 fichas iniciales](A01_S5_MATRIZ_SEMANTICA_RUTA_ACTIVA.md) + [16 nuevas TR-020…035](A01_S5_SEGUNDA_TANDA_CONTRATOS_Y_FRAGILIDADES.md), **35 por contrato/frontera**. Se añadió el [puente de nodeids y revisión de oráculos](A01_S5_PUENTE_NODEIDS_Y_ORACULOS.md) y su [analizador de solo lectura](map_a01_s5_nodeids.py). El [cruce con los JSON locales ya fue verificado](A01_S5_RESULTADO_PUENTE_NODEIDS_2026-11-15.md): 277 nodos en 29 archivos testigo y 1.197 en 144 archivos sin TR; ocho fuentes adicionales (236 nodos) tienen clasificación preliminar. **Nueva revisión granular:** [matriz de 33 variantes G3-B3](A01_S5_AUDITORIA_G3_B3_33_VARIANTES.md) por entradas, oráculos y SUT; [verificador de nodeids reales](verify_a01_s5_g3_b3_nodeids.py) preparado, pendiente de correr. **Aún hay 0 nodeids acreditados dinámicamente**; faltan otras funciones, falsación e independencia final. A-05 abierto; ningún cuerpo de test se ejecutó.
- **[A-05 — Colección real en clon separado](A05_PREFLIGHT_A01_COLECCION_AISLADA.md)** y [ejecutor opt-in](collect_a01_isolated.py) — **EN CURSO**: el owner ya recolectó pytest sobre el SHA `86cd6867`, con cuatro exit codes 0 y sin ejecutar cuerpos de tests. El clon **no** es una sandbox de seguridad del sistema operativo; faltan revisar logs y efectos de importación.
- **[Evidencia de colección A-01](A01_COLECCION_PYTEST_2026-11-15.md)** — **1.474** nodos `all`, **225** `unit`, **70** `integration_nonregression`, **1.454** `not e2e`. Falta conciliar JSON/markers/parametrizaciones y selección focal de CI; no es un PASS de tests.
- **[Plan maestro y casillas](PLAN_REMEDIACION_TESTS_PIPELINE.md#6-hoja-de-ruta-ejecutable-checkboxes-de-progreso)** — A-00 marcado `[x]`, etapas restantes pendientes.

## Primeros pasos

1. Revisar §3.2 del plan: inventario semilla `TS-001` a `TS-007`. Son hallazgos/inventario inicial, **no una auditoría exhaustiva**.
2. Ejecutar con seguridad **A-00 a A-07** y completar las fichas `TR-###` por caso de prueba.
3. Presentar al owner la matriz de brechas priorizada antes de implementar B.
4. Aportar evidence de las mutaciones negativas en C. No marcar casillas por tener CI o Pyright verde solamente.

## Reglas que no deben romperse

- **Contract first:** que los tests resistan refactors internos **sin** relajar invariantes funcionales.
- **Oráculos independientes:** ninguna comparación del resultado consigo mismo, ni autocreación de esperados en pytest.
- **Mocks en fronteras:** si se simula el SUT, no afirmar que se comprobó el SUT.
- **Sin efectos peligrosos:** tests aislados; no escribir ni editar corpus científico, fixtures históricas o PDFs locales del owner.
- **Sin cambios de runtime/CI ni merge automático:** el actual check requerido de GitHub y el CV científico informativo siguen igual.
- **Sin afirmaciones científicas:** tipado correcto, tests técnicos verdes y experimentos con fake no son certificación STEM.

## Referencias

- [Atlas de la ruta única](../pipeline-stabilization/handoff/ATLAS_RUTA_OPERATIVA_UNICA_PDF_PDF.md).
- [HITO 0.4.4 — regresión y tests](../phase-17-bis/00-foundation/HITO_0.4.4_REGRESSION_ARCHITECTURE_AUDIT.md).
- [HITO 4.4 — prerequisitos de tests](../phase-17-bis/00-foundation/HITO_4.4_TESTING_PREREQUISITES_DISCOVERY.md).
- [Hallazgos diferidos de Fase 17-BIS](../phase-17-bis/reports/FASE_17BIS_DEFERRED_FINDINGS_CONSOLIDATED.md).

**Punto de apertura:** sin tareas A/B/C completadas. La aprobación y la ejecución quedan sujetas a revisión del owner, evidencias por SHA y actualizaciones trazadas al plan.
