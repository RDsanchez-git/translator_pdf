"""POST-RUN VALIDATION (NADR-24 SS5.9 R36-R37, Wave 4.3 Task 4.3.4).

Functional Core: verificacion pura de post-condiciones sobre una
CertificationEvidence ya ensamblada y las identidades esperadas.
Toda violacion identifica el elemento faltante o inconsistente (R30/R37).
"""
from __future__ import annotations

from dataclasses import dataclass

from core.benchmark.certification.evidence import CertificationEvidence

ELEMENT_EVALUATION_PROVENANCE = "evaluation_provenance"
ELEMENT_PER_DOCUMENT_RESULTS = "per_document_results"
ELEMENT_AGGREGATE_RESULT = "aggregate_result"
ELEMENT_CORPUS_IDENTITY = "corpus_identity"
ELEMENT_MANIFEST_IDENTITY = "manifest_identity"
ELEMENT_CONFIGURATION_IDENTITY = "configuration_identity"
ELEMENT_FROZEN_PARAMETERS_IDENTITY = "frozen_parameters_identity"


@dataclass(frozen=True)
class PostRunViolation:
    element: str
    detail: str


@dataclass(frozen=True)
class PostRunReport:
    violations: tuple[PostRunViolation, ...]

    @property
    def is_pass(self) -> bool:
        return not self.violations


def validate_post_run(
    *,
    evidence: CertificationEvidence | None,
    expected_corpus_identity: str,
    expected_manifest_identity: str,
    expected_configuration_identity: str,
    expected_parameter_identity: str,
    manifest_document_ids: frozenset[str],
    evaluation_provenance_available: bool,
) -> PostRunReport:
    """Verifica (a) provenance, (b) per-document, (c) aggregate, (d) R29."""
    violations: list[PostRunViolation] = []

    # (a) Evaluation Provenance Record completo y verificable
    if not evaluation_provenance_available:
        violations.append(PostRunViolation(
            ELEMENT_EVALUATION_PROVENANCE,
            "Evaluation Provenance Record ausente o no verificable",
        ))

    if evidence is None:
        violations.append(PostRunViolation(
            ELEMENT_PER_DOCUMENT_RESULTS,
            "Certification Evidence ausente: no hay evidencia que validar",
        ))
        return PostRunReport(violations=tuple(violations))

    # (b) per-document evidence presente y biyectiva con el manifest
    evidenced_ids = frozenset(d.document_id for d in evidence.per_document_results)
    missing = manifest_document_ids - evidenced_ids
    orphan = evidenced_ids - manifest_document_ids
    if missing:
        violations.append(PostRunViolation(
            ELEMENT_PER_DOCUMENT_RESULTS,
            f"documentos sin veredicto: {sorted(missing)}",
        ))
    if orphan:
        violations.append(PostRunViolation(
            ELEMENT_PER_DOCUMENT_RESULTS,
            f"veredictos sin documento en manifest: {sorted(orphan)}",
        ))

    # (c) aggregate result presente
    if not evidence.aggregate_result:
        violations.append(PostRunViolation(
            ELEMENT_AGGREGATE_RESULT, "aggregate result vacio",
        ))

    # (d) identidades R29 completas y consistentes con las esperadas
    if not evidence.corpus_identity:
        violations.append(PostRunViolation(ELEMENT_CORPUS_IDENTITY, "identidad vacia"))
    elif evidence.corpus_identity != expected_corpus_identity:
        violations.append(PostRunViolation(
            ELEMENT_CORPUS_IDENTITY,
            f"identidad {evidence.corpus_identity} != esperada {expected_corpus_identity}",
        ))
    for element, actual, expected in (
        (ELEMENT_MANIFEST_IDENTITY, evidence.manifest_identity, expected_manifest_identity),
        (ELEMENT_CONFIGURATION_IDENTITY, evidence.configuration_identity, expected_configuration_identity),
        (ELEMENT_FROZEN_PARAMETERS_IDENTITY, evidence.frozen_parameters_identity, expected_parameter_identity),
    ):
        if not actual:
            violations.append(PostRunViolation(element, "identidad vacia"))
        elif actual != expected:
            violations.append(PostRunViolation(
                element, f"identidad {actual} != esperada {expected}",
            ))

    return PostRunReport(violations=tuple(violations))
