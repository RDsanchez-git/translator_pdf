import argparse
import time
from pathlib import Path
from bootstrap.topology import create_topology_evaluator
from experiments.reporting.jsonl_writer import JsonLinesReportWriter, ExperimentObservation
from experiments.loaders.ast_json_loader import load_ast_sequence_from_json

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ejecuta la suite de evaluadores topológicos sobre el corpus indicado."
    )
    parser.add_argument(
        "--corpus-dir",
        type=Path,
        default=Path("tests/corpus/calibration_v1"),
        help="Ruta al directorio raíz del corpus (debe contener 'ground_truth' y 'candidates')."
    )
    parser.add_argument(
        "--report-file",
        type=Path,
        default=Path("reports/scientific_significance_report.jsonl"),
        help="Ruta del archivo JSONL de salida para el reporte."
    )
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    corpus_dir = args.corpus_dir
    candidates_dir = corpus_dir / "candidates"
    gt_dir = corpus_dir / "ground_truth"
    report_file = args.report_file

    if not candidates_dir.exists() or not gt_dir.exists():
        print(f"[ERROR] Directorio de corpus incompleto en '{corpus_dir}'.")
        print(f"  - Ground Truth existe: {gt_dir.exists()} ({gt_dir})")
        print(f"  - Candidates existe:   {candidates_dir.exists()} ({candidates_dir})")
        return

    evaluator = create_topology_evaluator()
    report_file.parent.mkdir(parents=True, exist_ok=True)
    writer = JsonLinesReportWriter(report_file)

    parsers = [p.name for p in candidates_dir.iterdir() if p.is_dir()]
    if not parsers:
        print(f"[ERROR] No se encontraron subdirectorios de parsers candidatos en '{candidates_dir}'.")
        return

    print(f"Ejecutando benchmark experimental sobre parsers descubiertos: {parsers}")

    gt_files = list(gt_dir.glob("*.json"))
    if not gt_files:
        print(f"[WARNING] No se encontraron archivos JSON de Ground Truth en '{gt_dir}'.")
        return

    for gt_file in gt_files:
        doc_id = gt_file.stem
        gt_ast = load_ast_sequence_from_json(gt_file)

        for parser_name in parsers:
            cand_file = candidates_dir / parser_name / f"{doc_id}.json"
            if not cand_file.exists():
                print(f"[WARNING] Candidato no encontrado para '{parser_name}' / documento '{doc_id}' en '{cand_file}'.")
                continue

            cand_ast = load_ast_sequence_from_json(cand_file)

            start_time = time.perf_counter()
            score_dto = evaluator.evaluate(cand_ast, gt_ast)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            observation = ExperimentObservation(
                document_id=doc_id,
                parser_name=parser_name,
                score_dto=score_dto,
                candidate_node_count=len(cand_ast),
                ground_truth_node_count=len(gt_ast),
                execution_time_ms=elapsed_ms
            )

            writer.write(observation)
            print(f"[{parser_name}] Documento '{doc_id}': Score {score_dto.primary_score:.4f} ({elapsed_ms:.2f} ms)")

if __name__ == "__main__":
    main()