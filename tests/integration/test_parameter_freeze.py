"""Tests de integracion del entry point freeze_parameters (MIG-08).

NADR-23 SS5.6 R23-R25: freeze verificable e inmutable.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.evaluation.freeze_parameters import main

TS = '2026-09-10T12:00:00+00:00'


def _write_report(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        'corpus_verdict': 'HARD_FAIL',
        'corpus_nss': 0.6536,
        'pass_count': 1,
        'warning_count': 0,
        'hard_fail_count': 5,
    }), encoding='utf-8')


def _argv(tmp_path: Path, report: Path, out: Path, ts: str = TS) -> list[str]:
    return [
        '--corpus-dir', 'tests/corpus/canonical',
        '--evaluation-report', str(report),
        '--protocol-reference', 'FASE_5_WAVE_3_2_CALIBRATION_PROTOCOL_RECORD.md@1.0.0',
        '--timestamp', ts,
        '--evaluation-kind', 'SANITY_VALIDATION',
        '--limitation', 'H-5.3-1',
        '--limitation', 'H-5.3-2',
        '--output-dir', str(out),
    ]


def _argv_final(argv: list[str]) -> list[str]:
    out = list(argv)
    i = out.index('--evaluation-kind')
    out[i + 1] = 'FINAL_EVALUATION'
    return out


def test_freeze_materializes_artifacts_with_recomputable_identity(tmp_path: Path):
    report = tmp_path / 'report.json'
    _write_report(report)
    out = tmp_path / 'cal'
    assert main(_argv(tmp_path, report, out)) == 0

    freeze = json.loads((out / 'parameter_freeze.json').read_text(encoding='utf-8'))
    cal = json.loads((out / 'calibration_provenance_record.json').read_text(encoding='utf-8'))
    ev = json.loads((out / 'evaluation_provenance_record_SANITY_VALIDATION.json').read_text(encoding='utf-8'))

    # R18: cinco campos minimos presentes
    for field in ('corpus_identity', 'metric_configuration', 'parameters', 'result', 'timestamp'):
        assert field in cal

    # R24: identidad recalcularle desde el dominio coincide con el artefacto
    from bootstrap.topology import build_canonical_engine_configuration
    from core.benchmark.topology.criticality.costs import CriticalityAwareCostContext
    from core.benchmark.topology.regression.provenance import (
        FrozenParameters, ParameterIdentityCalculator)
    config = build_canonical_engine_configuration(cost_context=CriticalityAwareCostContext())
    recomputed = ParameterIdentityCalculator.calculate(FrozenParameters(
        config.nss_hard_fail, config.nss_warning, config.cost_weights, config.warning_threshold))
    assert freeze['parameter_identity'] == recomputed

    # R31: trazabilidad evaluation -> calibration via experiment identity
    assert ev['calibration_provenance_reference'] == cal['experiment_identity']
    assert ev['frozen_parameters_identity'] == freeze['parameter_identity']
    assert ev['limitations'] == ['H-5.3-1', 'H-5.3-2']
    assert cal['calibration_run'] == 'NONE'
    assert cal['parameters_origin'] == 'NORMATIVE_DESIGN'


def test_rerun_is_idempotent_noop(tmp_path: Path):
    report = tmp_path / 'report.json'
    _write_report(report)
    out = tmp_path / 'cal'
    assert main(_argv(tmp_path, report, out)) == 0
    before = (out / 'parameter_freeze.json').read_bytes()
    assert main(_argv(tmp_path, report, out, ts='2026-09-11T00:00:00+00:00')) == 0
    assert (out / 'parameter_freeze.json').read_bytes() == before


def test_conflict_returns_exit_2_without_writing(tmp_path: Path):
    report = tmp_path / 'report.json'
    _write_report(report)
    out = tmp_path / 'cal'
    assert main(_argv(tmp_path, report, out)) == 0
    freeze_path = out / 'parameter_freeze.json'
    data = json.loads(freeze_path.read_text(encoding='utf-8'))
    data['parameter_identity'] = '0' * 64
    freeze_path.write_text(json.dumps(data), encoding='utf-8')
    assert main(_argv_final(_argv(tmp_path, report, out, ts='2026-09-11T00:00:00+00:00'))) == 2
    assert not (out / 'evaluation_provenance_record_FINAL_EVALUATION.json').exists()


def test_final_evaluation_record_emitted_over_existing_freeze(tmp_path: Path):
    """Regresion del Riesgo 1: un run FINAL sobre freeze existente debe emitir
    su Evaluation Provenance Record (R31), no caer en no-op silencioso."""
    report = tmp_path / 'report.json'
    _write_report(report)
    out = tmp_path / 'cal'
    assert main(_argv(tmp_path, report, out)) == 0
    argv = _argv_final(_argv(tmp_path, report, out, ts='2026-09-12T00:00:00+00:00'))
    assert main(argv) == 0
    assert (out / 'evaluation_provenance_record_SANITY_VALIDATION.json').exists()
    assert (out / 'evaluation_provenance_record_FINAL_EVALUATION.json').exists()
    freeze_bytes = (out / 'parameter_freeze.json').read_bytes()
    assert main(argv) == 0
    assert (out / 'parameter_freeze.json').read_bytes() == freeze_bytes


def test_invalid_timestamp_returns_exit_2(tmp_path: Path) -> None:
    report = tmp_path / 'report.json'
    _write_report(report)
    out = tmp_path / 'cal'
    assert main(_argv(tmp_path, report, out, ts='sin-zona')) == 2


def test_missing_report_returns_exit_2_without_partial_state(tmp_path: Path) -> None:
    out = tmp_path / 'cal'
    assert main(_argv(tmp_path, tmp_path / 'nope.json', out)) == 2
    assert not out.exists() or not list(out.glob('*.json'))


REAL_FREEZE = Path('reports/calibration/parameter_freeze.json')


@pytest.mark.skipif(not REAL_FREEZE.exists(), reason='Artefacto de freeze no materializado')
def test_repo_freeze_artifact_matches_domain_defaults():
    from bootstrap.topology import build_canonical_engine_configuration
    from core.benchmark.topology.criticality.costs import CriticalityAwareCostContext
    from core.benchmark.topology.regression.provenance import (
        FrozenParameters, ParameterIdentityCalculator)
    config = build_canonical_engine_configuration(cost_context=CriticalityAwareCostContext())
    recomputed = ParameterIdentityCalculator.calculate(FrozenParameters(
        config.nss_hard_fail, config.nss_warning, config.cost_weights, config.warning_threshold))
    stored = json.loads(REAL_FREEZE.read_text(encoding='utf-8'))['parameter_identity']
    assert stored == recomputed, (
        'El artefacto de freeze no coincide con los defaults del dominio: '
        'nueva parameter identity => nueva linea de certificacion (NADR-23 R25).')
