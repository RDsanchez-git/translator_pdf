import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict
from core.benchmark.topology.models import MetricScoreDTO

@dataclass(frozen=True)
class ExperimentObservation:
    """DTO de la capa de experimentos para telemetría temporal y análisis de significancia."""
    document_id: str
    parser_name: str
    score_dto: MetricScoreDTO
    candidate_node_count: int
    ground_truth_node_count: int
    execution_time_ms: float

class JsonLinesReportWriter:
    """Serializa observaciones de evaluación directamente a formato JSONL."""

    def __init__(self, output_path: Path):
        self._output_path = output_path
        self._output_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, obs: ExperimentObservation) -> None:
        diagnostics_dict: Dict[str, Any] | None = None
        
        if obs.score_dto.diagnostics:
            # SOTA FIX: asdict() fuerza la deconstrucción recursiva de dataclasses anidados
            diagnostics_dict = asdict(obs.score_dto.diagnostics)

        record = {
            "document_id": obs.document_id,
            "parser": obs.parser_name,
            "metric_name": obs.score_dto.metric_name,
            "score": obs.score_dto.primary_score,
            "execution_ms": obs.execution_time_ms,
            "nodes_gt": obs.ground_truth_node_count,
            "nodes_cand": obs.candidate_node_count,
            "diagnostics": diagnostics_dict
        }

        with open(self._output_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")