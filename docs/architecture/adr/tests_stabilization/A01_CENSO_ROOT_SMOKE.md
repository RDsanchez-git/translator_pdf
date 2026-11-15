# A-01 — Inventario estático de declaraciones: raíz y smoke

> **Estado:** CENSO ESTÁTICO, NO colección real. Fuentes GitHub en `d638c35af2311fb05679aadee375ac2ac0450561`, sin ejecutar código. 8 módulos, 19 funciones `def test_*` detectadas. No se computan las expansiones de parametrización.

## Archivos y señales

| Archivo | Declaraciones | pytestmark en módulo (parcial) | Señales estáticas | Imports de código productivo (NO SUT acreditado) |
|---|---:|---|---|---|
| `tests/smoke/test_invariants_smoke.py` | 13 | — | — | core.validation.models |
| `tests/test_architecture_contract.py` | 2 | — | fileIO | infra.db.control_repo, infra.db.event_repo, infra.db.materialized_repo, core.execution.ports |
| `tests/test_ast.py` | 0 | — | — | — |
| `tests/test_dag.py` | 0 | — | — | — |
| `tests/test_fencing.py` | 0 | — | — | — |
| `tests/test_math_protector.py` | 1 | — | — | core.normalization.latex_sanitizer |
| `tests/test_pipeline.py` | 0 | — | fileIO | runtime.engine |
| `tests/test_pipeline_fidelity.py` | 3 | — | — | core.normalization.latex_sanitizer, core.ast.enums |

## Declaraciones detectadas

| Ubicación | Función declarada | Marcador cerca de la declaración (heurístico) | Parametrize cerca (heurístico) | Skip/xfail en cuerpo (heurístico) |
|---|---|---|---|---|
| `tests/smoke/test_invariants_smoke.py:15` | `test_smoke_si01_unclosed_brace` | — | — | — |
| `tests/smoke/test_invariants_smoke.py:20` | `test_smoke_si02_unbalanced_math` | — | — | — |
| `tests/smoke/test_invariants_smoke.py:24` | `test_smoke_si03_unclosed_environment` | — | — | — |
| `tests/smoke/test_invariants_smoke.py:31` | `test_smoke_pi01_doi_alteration` | — | — | — |
| `tests/smoke/test_invariants_smoke.py:35` | `test_smoke_pi02_url_domain_alteration` | — | — | — |
| `tests/smoke/test_invariants_smoke.py:40` | `test_smoke_pi03_orcid_lost` | — | — | — |
| `tests/smoke/test_invariants_smoke.py:44` | `test_smoke_pi04_cross_reference_lost` | — | — | — |
| `tests/smoke/test_invariants_smoke.py:51` | `test_smoke_pei01_markdown_block` | — | — | — |
| `tests/smoke/test_invariants_smoke.py:55` | `test_smoke_pei02_conversational_leak` | — | — | — |
| `tests/smoke/test_invariants_smoke.py:62` | `test_smoke_sei01_missing_number` | — | — | — |
| `tests/smoke/test_invariants_smoke.py:66` | `test_smoke_sei02_unit_mutation` | — | — | — |
| `tests/smoke/test_invariants_smoke.py:73` | `test_smoke_vi01_ratio_contraction` | — | — | — |
| `tests/smoke/test_invariants_smoke.py:79` | `test_smoke_vi01_ratio_expansion` | — | — | — |
| `tests/test_architecture_contract.py:9` | `test_ports_compliance` | — | — | — |
| `tests/test_architecture_contract.py:40` | `test_ast_node_instantiation_contract` | — | — | — |
| `tests/test_math_protector.py:9` | `test_inline_math_protector` | — | — | — |
| `tests/test_pipeline_fidelity.py:17` | `TestPipelineFidelity.test_semantic_adjacency_and_mutations` | — | — | — |
| `tests/test_pipeline_fidelity.py:33` | `TestPipelineFidelity.test_mixed_inline_and_block_math` | — | — | — |
| `tests/test_pipeline_fidelity.py:54` | `TestPipelineFidelity.test_worker_passthrough_alignment` | — | — | — |

## Límites

Este censo reconoce declaraciones por patrones de texto y permite localizar casos. **No** demuestra colección pytest, markers efectivos heredados, parametrizaciones expandidas, `unittest` parametrizado, fixtures autouse, skips dinámicos, SUT realmente ejecutado, red ni escritura real. `fileIO`/`external` son indicios para A-05, no operaciones observadas. La auditoría por SUT, independencia de oráculos y cobertura del pipeline corresponde a A-02/A-03, con colección sólo después de aislamiento A-05/A-06.
