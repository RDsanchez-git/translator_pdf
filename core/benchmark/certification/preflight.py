"""PREFLIGHT: tipos y evaluacion pura de precondiciones (NADR-24 SS5.2 R6-R9).

Functional Core: evaluate_preflight es pura y determinista (R9). Todo I/O
(manifest, artefactos, freeze) ocurre en el Imperative Shell
(tools/evaluation/preflight_certification.py), que inyecta resultados como datos.
El dominio NO importa infra ni composition root (Arquitectura Hexagonal).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PreflightCondition(Enum):
    """Ocho precondiciones normativas (R7 a-h)."""

    CORPUS_IDENTITY_MATCHES = "corpus_identity_matches"
    MANIFEST_FORMAT_VALID = "manifest_format_valid"
    GROUND_TRUTHS_SEALED = "ground_truths_sealed"
    ORACLE_HASHES_VERIFIABLE = "oracle_hashes_verifiable"
    CONFIGURATION_CANONICAL = "configuration_canonical"
    PARAMETERS_FROZEN = "parameters_frozen"
    CALIBRATION_PROVENANCE_AVAILABLE = "calibration_provenance_available"
    NO_PARTITION_LEAKAGE = "no_partition_leakage"


@dataclass(frozen=True)
class PreflightViolation:
    condition: PreflightCondition
    detail: str


@dataclass(frozen=True)
class PreflightReport:
    violations: tuple[PreflightViolation, ...]

    @property
    def is_pass(self) -> bool:
        return not self.violations


def evaluate_preflight(
    *,
    manifest_load_error: str | None,
    computed_manifest_hash: str | None,
    expected_manifest_hash: str,
    completeness_violations: tuple[str, ...],
    sealed_violations: tuple[str, ...],
    oracle_hash_violations: tuple[str, ...],
    current_configuration_identity: str,
    expected_configuration_identity: str,
    frozen_parameter_identity_in_artifact: str | None,
    expected_parameter_identity: str,
    calibration_provenance_available: bool,
    calibration_partition_identities: frozenset[str],
    corpus_sha256_identities: frozenset[str],
) -> PreflightReport:
    """Evalua las 8 precondiciones sobre datos ya cargados. Pura (R9)."""
    v: list[PreflightViolation] = []

    # (b) manifest cargable y formato vigente
    if manifest_load_error is not None:
        v.append(PreflightViolation(PreflightCondition.MANIFEST_FORMAT_VALID, manifest_load_error))
        return PreflightReport(violations=tuple(v))

    # (a) identidad del corpus verificada contra declarada (R11)
    if computed_manifest_hash != expected_manifest_hash:
        v.append(PreflightViolation(
            PreflightCondition.CORPUS_IDENTITY_MATCHES,
            f"manifest hash computado {computed_manifest_hash} != declarado {expected_manifest_hash}",
        ))

    # (c) GTs requeridos existen, biyeccion y estado Sealed
    for detail in completeness_violations:
        v.append(PreflightViolation(PreflightCondition.GROUND_TRUTHS_SEALED, detail))
    for detail in sealed_violations:
        v.append(PreflightViolation(PreflightCondition.GROUND_TRUTHS_SEALED, detail))

    # (d) oracle_hash verificables
    for detail in oracle_hash_violations:
        v.append(PreflightViolation(PreflightCondition.ORACLE_HASHES_VERIFIABLE, detail))

    # (e) configuracion canonica vigente
    if current_configuration_identity != expected_configuration_identity:
        v.append(PreflightViolation(
            PreflightCondition.CONFIGURATION_CANONICAL,
            f"configuration identity computada {current_configuration_identity} != declarada {expected_configuration_identity}",
        ))

    # (f) parametros congelados (artefacto presente y coincidente)
    if frozen_parameter_identity_in_artifact is None:
        v.append(PreflightViolation(
            PreflightCondition.PARAMETERS_FROZEN, "parameter_freeze.json ausente"))
    elif frozen_parameter_identity_in_artifact != expected_parameter_identity:
        v.append(PreflightViolation(
            PreflightCondition.PARAMETERS_FROZEN,
            f"parameter_identity en artefacto {frozen_parameter_identity_in_artifact} != declarada {expected_parameter_identity}",
        ))

    # (g) calibration provenance disponible
    if not calibration_provenance_available:
        v.append(PreflightViolation(
            PreflightCondition.CALIBRATION_PROVENANCE_AVAILABLE,
            "calibration_provenance_record.json ausente"))

    # (h) disjuncion por SHA-256 entre particion de calibracion y corpus
    # (Wave 3.1: CAL = vacio por H-5.3-1; el check es evaluable y no muerto)
    leakage = calibration_partition_identities & corpus_sha256_identities
    if leakage:
        v.append(PreflightViolation(
            PreflightCondition.NO_PARTITION_LEAKAGE,
            f"identidades en calibracion y corpus: {sorted(leakage)}"))

    return PreflightReport(violations=tuple(v))
