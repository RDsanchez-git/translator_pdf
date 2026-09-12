"""Codigos de salida uniformes para entry points (DF-18, NADR-24 SS5.4 R15-R19).

Taxonomia de tres categorias (R15):
  (a) EXIT_OK: ejecucion completada con resultado valido.
  (b) EXIT_CERTIFICATION_REJECTED: ejecucion completada, resultado cientifico
      valido pero rechazado (solo tooling de certificacion).
  (c) EXIT_EXECUTION_FAILURE: fallo de ejecucion/configuracion/integridad.

Nota de frontera: el dominio (core/) NUNCA importa este modulo. Solo la capa
CLI (tools/) lo consume. El dominio senala mediante excepciones tipadas; la
traduccion a exit codes ocurre exclusivamente en el Imperative Shell.
"""
from __future__ import annotations

EXIT_OK = 0
EXIT_CERTIFICATION_REJECTED = 1
EXIT_EXECUTION_FAILURE = 2
