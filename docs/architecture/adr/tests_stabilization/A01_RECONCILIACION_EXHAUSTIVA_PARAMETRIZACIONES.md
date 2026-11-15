# A-01 — Conciliación exhaustiva de 133 expansiones / 24 archivos

> **Estado:** **A01-S6 COMPLETADO**: explicación estática/dinámica de diferencias de recolección. **A-01 GLOBAL ABIERTO** por A01-S5 (contrato → SUT → mocks → aserción → falsador) y control A-05 independiente.
>
> **Fecha:** 2026-11-15. **SHA de los tests recolectados:** `86cd68672ee692f073b62869e7c9bd177e8d9e3b`.
>
> **Fuentes:** `all.json` / `manifest.json` de `translator-a01-isolated-k4f4mf10` analizados localmente por el owner con [`explain_a01_declaration_differences.py`](explain_a01_declaration_differences.py), salida íntegra aportada en la conversación, más lectura directa del archivo [`tests/unit/test_certification_boundary.py`](../../../../tests/unit/test_certification_boundary.py). **No** se ejecutó pytest ni se realizó una evaluación científica para producir esta conciliación.

## 1. Demostración de la identidad

| Métrica | Resultado | Interpretación |
|---|---:|---|
| Módulos `test_*.py` inspeccionados | **177** | Incluye 3 vacíos y 1 script manual |
| Declaraciones fuente de funciones `test_*` | **1.341** | Recuento AST de código fuente |
| Nodeids recolectados con `pytest --collect-only` | **1.474** | Selección real, no ejecución del cuerpo de test |
| Expansiones adicionales de nodeids de funciones que sí se recolectan | **+133** | Variantes de pruebas parametrizadas |
| Funciones de test declaradas y no recolectadas | **0** | Todas las 1.341 funciones fuente tienen correspondencia |
| Nodeids que carecen de función fuente correspondiente | **0** | No hay nodeids huérfanos en este cotejo |
| Diferencia neta | **+133** | **1.474 − 1.341 = 133 + 0 − 0**, identidad verificada |
| Archivos con diferencia | **24** | Suma de las 24 diferencias = **133** |
| Archivos `test_*.py` sin nodeids | **4** | 3 vacíos y 1 script manual; [clasificados](A01_COLECCION_PYTEST_2026-11-15.md#34-los-cuatro-módulos-sin-nodos-investigación-cerrada-2026-11-15) |

**Resultado:** no existe un *gap de colección* en las 1.341 funciones declaradas. **El resultado no permite concluir** que las pruebas se ejecuten con éxito, que protejan el contrato declarado, que sean suficientemente sensibles a mutaciones o que estén desacopladas de detalles internos del pipeline.

**Diferencia conceptual:** el informe anterior contabilizaba **187 ítems con `parameter_id`**; eso describe nodos que llevan parámetro, **no** 187 expansiones adicionales. La diferencia neta real es **133**, calculada a nivel de función/nodeid.

## 2. Matriz completa de las 24 diferencias

Las columnas `Funciones` y `Nodos` proceden del cotejo fuente→pytest. `+Δ` es el número adicional neto. **23/24 archivos** presentan longitudes de decoradores parametrizados literales que coinciden con todos sus ejemplos expandidos; en el restante, el origen es una constante de módulo inspeccionada. La columna de ámbito es una **clasificación preliminar**, no una acreditación de SUT o cobertura.

| # | Archivo | Funciones | Nodos | +Δ | Ámbito preliminar | Causa de expansión / comprobación |
|---:|---|---:|---:|---:|---|---|
| 1 | `tests/integration/test_g3_b3_structured_result_contract.py` | 12 | 33 | +21 | G3/B3 respuesta estructurada | 17 + 6 variantes en dos funciones; arrays literales; 0 anomalías |
| 2 | `tests/unit/test_b024_explicit_math_spans.py` | 4 | 18 | +14 | B02.4 matemática | 7 + 9 variantes; arrays literales; 0 anomalías |
| 3 | `tests/unit/test_w08_inference_identity_contract.py` | 8 | 21 | +13 | W08 identidad/reutilización | 4 + 11 variantes; arrays literales; 0 anomalías |
| 4 | `tests/unit/test_semantic_classification.py` | 7 | 17 | +10 | Efecto externo/UNKNOWN | 11 variantes de matriz; array literal; 0 anomalías |
| 5 | `tests/integration/test_g3_b4_3a_engine_staging.py` | 18 | 25 | +7 | G3 staging | 3 + 3 + 3 + 2 variantes en cuatro funciones; 0 anomalías |
| 6 | `tests/unit/test_b025_math_visual.py` | 8 | 15 | +7 | B02.5 imagen matemática | 8 variantes de familias tipográficas; array literal; 0 anomalías |
| 7 | `tests/unit/test_b032_offline_pdf_lab.py` | 9 | 16 | +7 | Laboratorio PDF offline | 6 + 3 variantes de rutas; arrays literales; 0 anomalías |
| 8 | `tests/unit/test_provenance_identities.py` | 12 | 19 | +7 | Tooling de identidad científica (diferido) | 4 + 5 variantes; arrays literales; 0 anomalías |
| 9 | `tests/unit/test_b022_image_rendering.py` | 6 | 12 | +6 | B02.2 asset gráfico | 7 variantes de ruta no canónica; array literal; 0 anomalías |
| 10 | `tests/integration/test_g3_b3_2_fenced_receipts.py` | 13 | 17 | +4 | G3 recibos durables | 4 + 2 variantes de fencing/estado; arrays literales; 0 anomalías |
| 11 | `tests/integration/test_g3_b4_3b_publication_recovery.py` | 17 | 21 | +4 | G3 publicación/recuperación | 4 + 2 variantes; arrays literales; 0 anomalías |
| 12 | `tests/integration/test_b024_g3_g5_math_roundtrip.py` | 2 | 5 | +3 | Preservación matemática G3→G5 | 4 variantes de delimitadores; array literal; 0 anomalías |
| 13 | `tests/integration/test_g3_b3_3a_staged_publication.py` | 13 | 16 | +3 | G3 publicación staged | 4 variantes de versión de proyección; array literal; 0 anomalías |
| 14 | `tests/integration/test_g3_b3_3b_finalization.py` | 20 | 23 | +3 | G3 finalización | 4 variantes de versión inválida; array literal; 0 anomalías |
| 15 | `tests/integration/test_g3_b4_9_reconciler_fencing.py` | 11 | 14 | +3 | G3 reconciliación/fencing | 4 variantes de autoridad obsoleta; array literal; 0 anomalías |
| 16 | `tests/unit/test_b0324_foreground_app_root.py` | 1 | 4 | +3 | CLI/foreground | 4 variantes de raíz de aplicación; array literal; 0 anomalías |
| 17 | `tests/unit/test_certification_boundary.py` | 7 | 10 | +3 | Tooling certificación (diferido) | 4 variantes desde constante de módulo CERTIFICATION_MODULES; 1 longitud no inferida, resuelta por lectura |
| 18 | `tests/unit/test_pymupdf_integrity.py` | 5 | 8 | +3 | B02 integridad PyMuPDF | 3 + 2 variantes; arrays literales; 0 anomalías |
| 19 | `tests/integration/test_g3_b4_2_ocr_router_durable_plan.py` | 8 | 10 | +2 | OCR→G3 plan durable | 2 + 2 variantes; arrays literales; 0 anomalías |
| 20 | `tests/integration/test_g3_b4_8_preserve_engine.py` | 1 | 3 | +2 | G3 preservación | 3 variantes; array literal; 0 anomalías |
| 21 | `tests/integration/test_g5_assembler_lease_recovery.py` | 12 | 14 | +2 | G5 lease/recovery | 3 variantes de recovery; array literal; 0 anomalías |
| 22 | `tests/integration/test_w08_durable_context_boundary.py` | 11 | 13 | +2 | W08 contexto durable | 3 variantes de manipulación de snapshot; array literal; 0 anomalías |
| 23 | `tests/unit/test_certification_evidence.py` | 16 | 18 | +2 | Tooling certificación (diferido) | 3 variantes de identidad; array literal; 0 anomalías |
| 24 | `tests/unit/test_zhang_shasha.py` | 15 | 17 | +2 | Algoritmo distancia AST | 3 variantes de escalabilidad; array literal; 0 anomalías |
| **TOTAL** | **24 archivos** | **236** | **369** | **+133** | — | **Identidad aritmética verificada** |

Los totales de `Funciones` y `Nodos` de la última fila son **solo para los 24 archivos con diferencia**, no para los 177 módulos. El resto de los archivos tiene diferencial neto cero.

## 3. La única longitud dinámica: `test_certification_boundary.py`

**Fuente verificada:** [`tests/unit/test_certification_boundary.py`](../../../../tests/unit/test_certification_boundary.py) líneas 25–30, 82–87.

```python
CERTIFICATION_MODULES = [
    REPO_ROOT / "core" / "benchmark" / "certification" / "contract.py",
    REPO_ROOT / "core" / "benchmark" / "certification" / "preflight.py",
    REPO_ROOT / "tools" / "evaluation" / "preflight_certification.py",
    REPO_ROOT / "tools" / "evaluation" / "freeze_parameters.py",
]

@pytest.mark.parametrize("module_path", CERTIFICATION_MODULES, ids=lambda p: p.name)
def test_no_forbidden_gt_write_symbols(self, module_path: Path) -> None:
    ...
```

El analizador reportó `source_parametrize_lengths=[null]` porque el segundo argumento es un **`ast.Name`**, no una lista directamente insertada en el decorador. **El nombre resuelve a una lista visible de cuatro rutas**; los cuatro nodos recolectados coinciden exactamente con esa cardinalidad. **No se modifica el test ni el artefacto freeze.** Este módulo trata fronteras de certificación/GT y permanece fuera del alcance activo de esta campaña.

## 4. Decisión de cierre y transición a auditoría semántica

- [x] Las **24 diferencias** han quedado explicadas, con suma **+133**.
- [x] **0 funciones fuente no recolectadas, 0 nodeids huérfanos** según el cruce por nombre.
- [x] **23 archivos** tienen coincidencia literal de longitud de parametrizaciones; **1** utiliza la lista nombrada `CERTIFICATION_MODULES` con **4 entradas**.
- [x] Se conserva la distinción `pytest --collect-only` frente a test PASSED.
- [x] Se preservan los tres placeholders vacíos y el script `tests/test_pipeline.py` sin convertirlos en cobertura.
- [ ] **A01-S5:** construir fichas por contrato observable y componente productivo **realmente ejecutado**, registrar dobles y límites, aserciones y defecto que debería detectar. Priorizar G3/G5/W06/OCR/CLI y distinguir R1/benchmark/GT (diferidos).
- [ ] **A05-P4/P6:** seguridad de imports, plugins, red a nivel OS y archivos ignorados/efectos fuera de Git aún pendientes.

**Regla de diseño para etapa siguiente:** un contrato durable y agnóstico a refactor se protege con entradas/salidas/estado observable, testigos negativos independientes y dobles ubicados en fronteras externas. **No** reescribir tests para igualar conteos ni ajustar oráculos para obtener resultados verdes. La auditoría semántica comienza con clasificación por SUT y falsador, no con cambios de producción.

**Gobierno:** solo documentación bajo `docs/architecture/adr/tests_stabilization/`; `main`, producción, tests, CI, snapshots y GT permanecen sin modificaciones. El PDF deliberadamente eliminado en working tree local del owner queda fuera de esta campaña.
