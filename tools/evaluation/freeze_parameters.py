"""tools/evaluation/freeze_parameters.py

Entry point CLI para el parameter freeze (MIG-08, NADR-23 SS5.6 R23-R25) y
la emision de Calibration Provenance Record (SS5.5 R18-R22) y Evaluation
Provenance Record (SS5.8 R29-R31).

Functional Core: los calculadores de identidad viven en el dominio
(core/benchmark/topology/regression/provenance.py). Este entry point es el
Imperative Shell: I/O, timestamps y codigos de salida.

Semantica de fallo (consistente con DF-18, sin fallos silenciosos):
  exit 0 = freeze materializado, o no-op idempotente (freeze identico previo)
  exit 1 = violacion de contrato (timestamp invalido, manifest ausente,
           reporte de evaluacion ausente o incompleto)
  exit 2 = conflicto de freeze (artefacto existente con parameter identity
           distinta => nueva linea de certificacion obligatoria, R25)

Semantica de escritura:
  - evaluation record: SIEMPRE se emite, nombre acotado por evaluation_kind
    (latest-emission-wins; la trazabilidad apunta a result_identity, no al
    archivo del record).
  - freeze + calibration record: solo en primera emision (idempotencia R33).
  - conflicto de freeze: chequeo de solo lectura, estrictamente antes de
    cualquier escritura (cero estado parcial).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Sequence

from bootstrap.topology import build_canonical_engine_configuration
from core.benchmark.topology.criticality.costs import CriticalityAwareCostContext
from core.benchmark.topology.regression.configuration import (
    ConfigurationFingerprintCalculator,
)
from core.benchmark.topology.regression.provenance import (
    CalibrationProvenanceRecord,
    EvaluationProvenanceRecord,
    ExperimentIdentityCalculator,
    FrozenParameters,
    ParameterIdentityCalculator,
    ResultIdentityCalculator,
)
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader

EXIT_OK = 0
EXIT_CONTRACT_VIOLATION = 1
EXIT_FREEZE_CONFLICT = 2

FREEZE_FILENAME = 'parameter_freeze.json'
CALIBRATION_FILENAME = 'calibration_provenance_record.json'
EVALUATION_FILENAME_TEMPLATE = 'evaluation_provenance_record_{}.json'


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Parameter freeze y emision de provenance records (MIG-08).'
    )
    parser.add_argument('--corpus-dir', type=Path, required=True)
    parser.add_argument('--evaluation-report', type=Path, required=True,
                        help='Reporte JSON de la evaluacion (sanity o final).')
    parser.add_argument('--protocol-reference', required=True,
                        help='Identidad del protocolo aprobado (documento@version).')
    parser.add_argument('--timestamp', required=True,
                        help='Timestamp ISO-8601 con timezone (inyectado, R18/R20).')
    parser.add_argument('--evaluation-kind', default='SANITY_VALIDATION',
                        choices=['SANITY_VALIDATION', 'FINAL_EVALUATION'])
    parser.add_argument('--limitation', action='append', default=[],
                        help='ID de hallazgo/limitacion conocida (repetible).')
    parser.add_argument('--output-dir', type=Path, default=Path('reports/calibration'))
    return parser.parse_args(argv)


def _validate_timestamp(raw: str) -> str:
    """Fail-fast ante timestamp ausente de zona horaria (determinismo)."""
    normalized = raw.replace('Z', '+00:00') if raw.endswith('Z') else raw
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f'Timestamp ISO-8601 invalido: {raw!r}') from exc
    if parsed.tzinfo is None:
        raise ValueError(f'Timestamp sin timezone no aceptado: {raw!r}')
    return parsed.isoformat()


def _write_json(path: Path, mapping: dict[str, object]) -> None:
    path.write_text(
        json.dumps(mapping, indent=2, ensure_ascii=False, sort_keys=True),
        encoding='utf-8',
        newline='\n',
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    # 1. Timestamp (R18: campo obligatorio; R20: no participa en identidades)
    try:
        timestamp = _validate_timestamp(args.timestamp)
    except ValueError as exc:
        print(f'[ERROR] {exc}', file=sys.stderr)
        return EXIT_CONTRACT_VIOLATION

    # 2. corpus_identity desde el manifest (reutilizacion estricta)
    try:
        loader = LocalFileSystemCorpusLoader(base_path=args.corpus_dir)
        manifest_dto = loader.load_raw_manifest()
    except FileNotFoundError as exc:
        print(f'[ERROR] Manifest no encontrado: {exc}', file=sys.stderr)
        return EXIT_CONTRACT_VIOLATION
    corpus_identity = manifest_dto.manifest_hash

    # 3. Reporte de evaluacion: result_identity + resumen (fail-fast si falta)
    report_path: Path = args.evaluation_report
    if not report_path.exists():
        print(f'[ERROR] Reporte de evaluacion no encontrado: {report_path}', file=sys.stderr)
        return EXIT_CONTRACT_VIOLATION
    report_bytes = report_path.read_bytes()
    result_identity = ResultIdentityCalculator.calculate_from_bytes(report_bytes)
    try:
        report_data = json.loads(report_bytes.decode('utf-8'))
        summary = (
            f"{args.evaluation_kind}: corpus_verdict={report_data['corpus_verdict']}; "
            f"corpus_nss={report_data['corpus_nss']}; pass={report_data['pass_count']}; "
            f"warning={report_data['warning_count']}; hard_fail={report_data['hard_fail_count']}"
        )
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError) as exc:
        print(f'[ERROR] Reporte de evaluacion incompleto o invalido: {exc}', file=sys.stderr)
        return EXIT_CONTRACT_VIOLATION

    # 4. Configuracion canonica y parametros (fuente unica: composition root)
    config = build_canonical_engine_configuration(cost_context=CriticalityAwareCostContext())
    configuration_identity = ConfigurationFingerprintCalculator.calculate(config)
    parameters = FrozenParameters(
        nss_hard_fail=config.nss_hard_fail,
        nss_warning=config.nss_warning,
        cost_weights=config.cost_weights,
        warning_threshold=config.warning_threshold,
    )
    parameter_identity = ParameterIdentityCalculator.calculate(parameters)
    experiment_identity = ExperimentIdentityCalculator.calculate(
        corpus_identity=corpus_identity,
        protocol_identity=args.protocol_reference,
        configuration_identity=configuration_identity,
    )

    # 5. Registros puros (R18/R31): construccion antes de cualquier escritura
    calibration_record = CalibrationProvenanceRecord(
        corpus_identity=corpus_identity,
        metric_configuration=configuration_identity,
        parameters=parameters,
        result=summary,
        timestamp=timestamp,
        parameter_identity=parameter_identity,
        experiment_identity=experiment_identity,
        result_identity=result_identity,
        protocol_identity=args.protocol_reference,
        calibration_run='NONE',
        parameters_origin='NORMATIVE_DESIGN',
    )
    evaluation_record = EvaluationProvenanceRecord(
        corpus_identity=corpus_identity,
        configuration_identity=configuration_identity,
        frozen_parameters_identity=parameter_identity,
        result=summary,
        timestamp=timestamp,
        result_identity=result_identity,
        evaluation_kind=args.evaluation_kind,
        calibration_provenance_reference=experiment_identity,
        limitations=tuple(args.limitation),
    )

    # 6. Conflicto de freeze (R25): solo lectura, estrictamente antes de escribir
    args.output_dir.mkdir(parents=True, exist_ok=True)
    freeze_path = args.output_dir / FREEZE_FILENAME
    first_emission = not freeze_path.exists()
    if not first_emission:
        existing = json.loads(freeze_path.read_text(encoding='utf-8'))
        existing_identity = existing.get('parameter_identity')
        if existing_identity != parameter_identity:
            print(
                f'[ERROR] Conflicto de freeze: parameter_identity existente '
                f'{existing_identity} distinta de la actual {parameter_identity}. '
                f'Nueva linea de certificacion obligatoria (NADR-23 SS5.6 R25).',
                file=sys.stderr,
            )
            return EXIT_FREEZE_CONFLICT

    # 7. Escrituras: evaluation record SIEMPRE (artefacto por run/kind,
    #    latest-emission-wins; la trazabilidad apunta a result_identity, no al
    #    archivo del record). freeze + calibration record solo en primera
    #    emision (idempotencia, R33).
    eval_path = args.output_dir / EVALUATION_FILENAME_TEMPLATE.format(args.evaluation_kind)
    _write_json(eval_path, evaluation_record.to_mapping())
    if first_emission:
        _write_json(freeze_path, {
            'parameter_identity': parameter_identity,
            'configuration_identity': configuration_identity,
            'corpus_identity': corpus_identity,
            'parameters': calibration_record.to_mapping()['parameters'],
            'frozen_at': timestamp,
            'immutability_rule': (
                'NADR-23 SS5.6 R25: toda nueva configuracion constituye una nueva '
                'parameter identity y requiere una nueva linea de certificacion.'
            ),
        })
        _write_json(args.output_dir / CALIBRATION_FILENAME, calibration_record.to_mapping())
        print('[OK] Parameter freeze materializado (MIG-08).')
    else:
        print('[OK] Freeze identico ya materializado. No-op idempotente; '
              f'Evaluation Provenance Record emitido para este run ({args.evaluation_kind}).')
    print(f'  parameter_identity:      {parameter_identity}')
    print(f'  configuration_identity:  {configuration_identity}')
    print(f'  experiment_identity:     {experiment_identity}')
    print(f'  result_identity:         {result_identity}')
    print(f'  Artefactos en: {args.output_dir}')
    return EXIT_OK


if __name__ == '__main__':
    sys.exit(main())
