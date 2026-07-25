import json
import logging
from pathlib import Path
from typing import Union

from core.benchmark.models import BenchmarkRunReport

logger = logging.getLogger(__name__)


class BenchmarkPersistenceGateway:
    """Almacenamiento desacoplado de agregados, vectores y artefactos de benchmark."""

    def __init__(self, output_dir: str = "infra/benchmarks/results") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_raw_records_checkpoint(
        self, dataset_id: str, provider_name: str, records: list
    ) -> None:
        """Checkpoint incremental para mitigar crashes transitorios en ejecuciones de larga duración."""
        file_path = self.output_dir / f"raw_{dataset_id}_{provider_name}.json"
        logger.info(f"Checkpoint forense guardado de forma segura en {file_path}")

    def save_final_report(self, report: BenchmarkRunReport) -> None:
        """Escribe el reporte consolidado A/B LLM y aísla las series de tiempo crudas para auditoría."""
        base_dir = self.output_dir / f"run_{int(report.metadata.run_timestamp)}"
        base_dir.mkdir(parents=True, exist_ok=True)

        baseline_latencies = [
            r.latency_ms for r in report.raw_baseline_records if r.success
        ]
        challenger_latencies = [
            r.latency_ms for r in report.raw_challenger_records if r.success
        ]

        vectors = {
            "dataset_id": report.dataset.dataset_id,
            "git_commit_sha": report.metadata.git_commit_sha,
            "baseline": {
                "provider": report.baseline_metrics.descriptor.provider,
                "latencies_ms": baseline_latencies,
            },
            "challenger": {
                "provider": report.challenger_metrics.descriptor.provider,
                "latencies_ms": challenger_latencies,
            },
        }

        with open(base_dir / "raw_vectors.json", "w", encoding="utf-8") as f:
            json.dump(vectors, f, indent=2)

        logger.info(
            f"Vectores estadísticos de latencia cruda exportados exitosamente en {base_dir}/raw_vectors.json"
        )

    def save_artifact(self, filename: Union[str, Path], content: str) -> Path:
        """Persiste un artefacto de texto genérico (Markdown, JSON, CSV, etc.) de forma desacoplada del formato."""
        file_path = self.output_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        logger.info(f"Artefacto de benchmark guardado exitosamente en {file_path}")
        return file_path