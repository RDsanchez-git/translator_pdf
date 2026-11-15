# A01-S5 — Puente reproducible entre 1.474 nodeids y 35 fichas semánticas

> **Estado:** MÉTODO VERSIONADO y **ejecutado por el owner**; la [partición 277/1.197 y el triaje inicial](A01_S5_RESULTADO_PUENTE_NODEIDS_2026-11-15.md) están registrados. **No** implica mapeo semántico individual ni tests ejecutados. A01-S5 / A-01 / A-05 siguen abiertos.
>
> **Fecha:** 2026-11-15. **SHA de colección fijado:** `86cd68672ee692f073b62869e7c9bd177e8d9e3b`. Fuente documental: [primera tanda TR-001…019](A01_S5_MATRIZ_SEMANTICA_RUTA_ACTIVA.md) y [segunda tanda TR-020…035](A01_S5_SEGUNDA_TANDA_CONTRATOS_Y_FRAGILIDADES.md). Fuente de nodos: `all.json` / `manifest.json` generados por la colección aislada en el ordenador del owner.
>
> **Restricción:** ningún test, pipeline, workflow CI, baseline, corpus o GT ha sido modificado en esta fase. La colección real fue `--collect-only`; no hay pruebas PASSED ni mutaciones acreditadas.

## 1. Problema de trazabilidad y definición de cobertura

Las **35 fichas TR** describen contratos o fronteras y a menudo agrupan **múltiples funciones**. No representan 35 módulos distintos ni garantizan la protección de todos los casos que pytest reconoce. El inventario recolectó **1.474 nodeids únicos**, de los cuales **1.159 no declaran marker de nivel**. Una marca ausente no equivale a exclusión del CI, y `not e2e` no equivale a «únicamente ruta PDF→PDF».

Se fija la jerarquía:

1. **Nodeid (hecho):** un ítem concreto de `all.json`, con `file::test[...] `, markers y parámetros.
2. **Archivo asociado a TR (candidato):** el archivo aparece en la matriz. **No acredita** que todos sus tests protejan esa frontera.
3. **Función → contrato/SUT (auditoría estática):** lectura individual del test y del puerto realmente invocado. Debe registrar dobles, aserciones, salida observable y anomalías.
4. **Independencia de oráculo (A-03):** comprobar que el expected no procede del actual ni del mismo SUT no confiable; no aceptar tautologías.
5. **Sensibilidad (C):** test válido que falla por la razón prevista tras una violación contractual controlada en sandbox descartable.

**Está prohibido** utilizar la categoría `CONFIABLE_PARA_SU_ALCANCE` por el mero paso 1, 2 o 3.

## 2. Herramienta de solo lectura

[`map_a01_s5_nodeids.py`](map_a01_s5_nodeids.py) realiza exclusivamente operaciones de lectura y genera **JSON por stdout**, sin crear archivos:

- Verifica que el reporte corresponde al SHA congelado; tiene 1.474 nodeids únicos y los conteos del manifiesto son consistentes.
- Verifica **mediante Git** que los archivos bajo `tests/` versionados no cambiaron entre aquel commit y `HEAD`, ni en el índice o working tree. **No detecta** archivos ignorados o no rastreados, ni efectos en rutas externas.
- Extrae las 35 fichas desde las tablas Markdown, sus rutas de fuente y cinco referencias explícitas a «mismo archivo» (`TR-002→001`, `TR-007→006`, `TR-010→009`, `TR-014/015→013`). **Se verificó contra los documentos que son 35 fichas y 29 archivos distintos**, pero falta ejecutar la conciliación sobre el JSON local.
- Particiona cada nodeid en **archivo testigo documentado** o **archivo aún no documentado**. No se da cobertura semántica a ningún nodeid por asociación automática.
- Calcula cantidad de archivos testigo, nodos por archivo, nodos sin marker de nivel y archivos no documentados más poblados para priorizar inspección.
- Registra hallazgos de fuentes con evidencia estática directa; jamás lee ficheros de GT o ejecuta scripts peligrosos.

### Ejecución en PowerShell del owner (no ejecuta pytest)

```powershell
git pull --ff-only origin tests_stabilization

$reports = Join-Path $env:TEMP "translator-a01-isolated-k4f4mf10\reports"

.\venv\Scripts\python.exe .\docs\architecture\adr\tests_stabilization\map_a01_s5_nodeids.py --repo-root . --reports $reports --top 18
```

**Salida solicitada para registrar evidencia:** `test_nodeids_total`, `documented_contract_fichas`, `distinct_documented_witness_files`, `nodeids_in_documented_witness_FILES_not_semantically_verified`, `nodeids_in_other_FILES_pending_review`, `without_level_marker_total`, `files_without_TR_refs_top`, `source_confirmed_quality_alerts` y `checks`. Si produce error, no deshabilitar el guard para ocultarlo; informar el error literal y corregir la causa.

**Sin comandos de limpieza, restauración ni modificación del PDF intencionalmente eliminado**. El ejecutor no crea un clon ni invoca pytest; reutiliza únicamente evidencias existentes.

## 3. Hallazgos semánticos de fuentes ya confirmados — no «PASS»

| ID | Archivo | Hecho visible en fuente | Clasificación provisional | Corrección durable candidata, sólo en fase B |
|---|---|---|---|---|
| **H-S5-01** | `tests/integration/test_golden_parser.py` | `patch.object(adapter, 'parse', ...) ` y `expected_fingerprint = current_fingerprint`; si falta golden hace `skipTest`; setup puede escribir un «dummy PDF» | **Defectuoso para su pretensión de oráculo/parser real** | Reemplazar expected autorreferente por **invariantes técnicas independientes y SUT real**. No requerir ni alterar GT científico; los ficheros obligatorios no se autogeneran ni se convierten en SKIP silencioso |
| **H-S5-02** | `tests/integration/test_chunker_snapshot.py` | Si falta el snapshot, **lo escribe y retorna**; de 11 campos serializados solo comprueba unos pocos, y su caché AST puede faltar con SKIP | **Defectuoso como guard de snapshot inmutable** | Separar generación gobernada de verificación; expected técnico sellado/independiente o invariantes de dominio estables, no detalles accidentales por defecto |
| **H-S5-03** | `tests/integration/test_real_parser_pipeline.py` | Sustituye `adapter.parse` por `mock_nodes` dentro del test presentado como parser real | **Limitado/mal nombrado para la cobertura pretendida** | Mantener el test útil de modelo/control, o reorientarlo al **parser real** con PDFs sintéticos independientes; no confundirlo con `test_verification_pipeline_connection.py`, que sí invoca el parser |
| **H-S5-04** | `tests/integration/test_real_e2e.py` | Sustituye `self.pipeline.execute` por `mock_result` en la prueba de «ejecución real» | **Limitado/mal nombrado como E2E** | Conservar la validación de consumidor/FinOps si aporta valor, pero atribuirle alcance acotado; no fabricar otro E2E ni declarar runtime real |

**Regla de priorización:** H-S5-01 y H-S5-02 son falsas garantías **confirmadas por lectura de fuente**, no defectos nuevos descubiertos por ejecutar tests. H-S5-03/H-S5-04 presentan *desajustes de alcance*, no son pruebas inútiles automáticamente. Ninguna de estas conclusiones autoriza implementar B antes de cerrar el gate de A.

## 4. Prioridad para la revisión semántica siguiente

La ejecución del puente permitirá ordenar **archivos no documentados por volumen real de nodeids**, evitando inferir que todo lo no mapeado es de la ruta activa. Una vez recibidos esos datos, para cada familia se decidirá entre:

- **ACTIVA:** protege entradas, puertos y efectos observables de CLI/inbox, OCR/AST, G3/W06, G5/PDF.
- **TÉCNICA COMPARTIDA:** estructura AST, math, imágenes, storage y contratos de dominio reutilizados.
- **LEGACY / HISTÓRICA:** R1, R3 o test de una API cuyo soporte como entrypoint terminó; clasificar por SUT, no por nombre.
- **CIENCIA / GT / CV DIFERIDA:** inventariar y conservar sin rebaseline, umbrales ni ejecución científica.
- **DESCONOCIDA:** sin prueba suficiente de alcance o independencia; queda pendiente.

**Preferencia de ingeniería:** contrato observable en la frontera, inyección de dobles sólo para dependencias externas, expected independiente y tests que sobrevivan a refactors. Se preserva todo control de leasing, identidad generacional, no repetición de efectos externos y no publicación falsa.

## 5. Gates y seguimiento

- [x] **S5-N1:** matriz de **35 fichas** existente con archivo y frontera. Cinco relaciones «mismo archivo» comprobadas y **29 archivos testigo distintos**.
- [x] **S5-N2:** [herramienta de solo lectura](map_a01_s5_nodeids.py) añadida con guard SHA/working tree de tests y clasificación conservadora; **su corrida real está pendiente**.
- [x] **S5-N3:** documentados **cuatro hallazgos estáticos** por inspección de fuente, separados entre falsos oráculos y exceso de alcance.
- [x] **S5-N4:** owner ejecutó la herramienta sobre `all.json`; [reporte documentado](A01_S5_RESULTADO_PUENTE_NODEIDS_2026-11-15.md). 1.474 nodos, 277 en 29 archivos testigo, 1.197 en otros 144, 0 semánticamente acreditados.
- [ ] **S5-N5:** ampliar las fichas a los nodeids relevantes (no acreditar automáticamente todos los nodos de un archivo).
- [ ] **S5-N6:** auditar oráculos A-03 de los candidatos a intervención B, incluyendo falsadores y sensibilidad para C.
- [ ] **S5-N7:** clasificar ámbito de los casos no activos, sin evaluar ni modificar GT.
- [ ] **A01-S5 / A-01:** **ABIERTO**; A-05-P4/P6 y el aislamiento OS también están abiertos.

**Condición de cierre:** una lista de nodeids relevantes y su contrato, SUT real, dobles, expected independiente, defecto falsador y categoría **provisional** reproducible. A-03 y C podrán elevarla sólo con evidencia dinámica apropiada.
