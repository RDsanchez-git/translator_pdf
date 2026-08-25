"""Módulo de servicios de dominio del bounded context ground_truth.

NADR-14 §5.2 R4: autoridad única de sellado. El servicio duplicado
`ManifestGroundTruthUpdater` fue eliminado (Zero Debt, E-2.0-03).

Historial de responsabilidades migradas:
- Política de actualización de linaje → `ManifestLineageSealer`
  (core/benchmark/corpus/services.py, autoridad única en corpus)
- Integración con autoridad de sellado → `SealGroundTruthUseCase`
  (core/benchmark/ground_truth/use_cases.py)

Este archivo se mantiene como placeholder para futuros servicios de
dominio del bounded context ground_truth.
"""