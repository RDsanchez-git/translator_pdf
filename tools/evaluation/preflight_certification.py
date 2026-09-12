"""Entry point CLI de PREFLIGHT (NADR-24 SS5.2 R6-R9, Task 4.1.2).

Imperative Shell: todo I/O ocurre aqui; el dominio solo evalua datos puros.
Cuatro argumentos required (R10/R11). Exit codes: 0 = OK; 2 = violacion (R8).
Idempotente por construccion (R9): solo lecturas y hashes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from bootstrap.topology import build_canonical_engine_configuration
from core.benchmark.certification.preflight import evaluate_preflight
from core.benchmark.corpus.services import ManifestFingerprintCalculator
from core.benchmark.corpus.use_cases import LoadCorpusManifestUseCase
from core.benchmark.ground_truth.errors import IncompleteBaselineError
from core.benchmark.ground_truth.models import GroundTruthLifecycleState
from core.benchmark.topology.criticality.costs import CriticalityAwareCostContext
from core.benchmark.topology.regression.adapter import RegressionAdapter
from core.benchmark.topology.regression.configuration import (
    ConfigurationFingerprintCalculator,
)
from core.shared.exit_codes import EXIT_EXECUTION_FAILURE, EXIT_OK
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader
from infra.fs.ground_truth_store import LocalFileSystemGroundTruthArtifactAdapter
from tools.evaluation.entry_guard import run_entry


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PREFLIGHT de certificacion: verifica 8 precondiciones normativas."
    )
    parser.add_argument("--corpus-dir", type=Path, required=True)
    parser.add_argument("--expected-manifest-hash", type=str, required=True)
    parser.add_argument("--expected-configuration-identity", type=str, required=True)
    parser.add_argument("--expected-parameter-identity", type=str, required=True)
    parser.add_argument("--calibration-dir", type=Path, default=Path("reports/calibration"))
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    # (a)+(b) carga de manifest via puerto/use case
    manifest_load_error: str | None = None
    computed_hash: str | None = None
    sealed_violations: list[str] = []
    oracle_violations: list[str] = []
    corpus_sha: frozenset[str] = frozenset()
    manifest = None
    try:
        loader = LocalFileSystemCorpusLoader(base_path=args.corpus_dir)
        manifest = LoadCorpusManifestUseCase(reader=loader).execute()
        computed_hash = ManifestFingerprintCalculator.compute_hash(
            manifest.corpus_version, list(manifest.documents)
        )
        sealed_value = GroundTruthLifecycleState.SEALED.value
        for doc in manifest.documents:
            if doc.ground_truth_state != sealed_value:
                sealed_violations.append(f"{doc.document_id} no esta en estado sealed")
            if not doc.oracle_hash:
                oracle_violations.append(f"{doc.document_id} sin oracle_hash")
        corpus_sha = frozenset(doc.fingerprint.sha256 for doc in manifest.documents)
    except Exception as e:  # manifest ausente/invalido => precondicion (b)
        manifest_load_error = f"manifest no cargable en {args.corpus_dir}: {e}"

    # (c) completitud biyectica: verify_completeness RAISE (F4)
    completeness_violations: tuple[str, ...] = ()
    if manifest is not None:
        try:
            artifact_adapter = LocalFileSystemGroundTruthArtifactAdapter(base_path=args.corpus_dir)
            RegressionAdapter().verify_completeness(
                frozenset(d.document_id for d in manifest.documents),
                frozenset(artifact_adapter.list_artifact_ids()),
            )
        except IncompleteBaselineError as e:
            completeness_violations = (str(e),)

    # (e) identidad de configuracion vigente (composition root, solo en Shell)
    config = build_canonical_engine_configuration(cost_context=CriticalityAwareCostContext())
    current_config_id = ConfigurationFingerprintCalculator.calculate(config)

    # (f)+(g) artefactos de freeze y provenance
    freeze_path = args.calibration_dir / "parameter_freeze.json"
    frozen_id_in_artifact: str | None = None
    if freeze_path.exists():
        frozen_id_in_artifact = json.loads(
            freeze_path.read_text(encoding="utf-8")
        ).get("parameter_identity")
    provenance_available = (
        args.calibration_dir / "calibration_provenance_record.json"
    ).exists()

    report = evaluate_preflight(
        manifest_load_error=manifest_load_error,
        computed_manifest_hash=computed_hash,
        expected_manifest_hash=args.expected_manifest_hash,
        completeness_violations=completeness_violations,
        sealed_violations=tuple(sealed_violations),
        oracle_hash_violations=tuple(oracle_violations),
        current_configuration_identity=current_config_id,
        expected_configuration_identity=args.expected_configuration_identity,
        frozen_parameter_identity_in_artifact=frozen_id_in_artifact,
        expected_parameter_identity=args.expected_parameter_identity,
        calibration_provenance_available=provenance_available,
        # Wave 3.1 / H-5.3-1: particion de calibracion vacia por estrategia aprobada
        calibration_partition_identities=frozenset(),
        corpus_sha256_identities=corpus_sha,
    )

    if report.is_pass:
        print("[PREFLIGHT] All 8 conditions satisfied")
        return EXIT_OK
    for violation in report.violations:
        print(f"[PREFLIGHT-{violation.condition.value}] {violation.detail}", file=sys.stderr)
    return EXIT_EXECUTION_FAILURE


if __name__ == "__main__":
    run_entry(main)
