import logging
import pathlib
from core.benchmark.ground_truth.use_cases import SealGroundTruthUseCase
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader
from infra.fs.ground_truth_store import LocalFileSystemGroundTruthArtifactAdapter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("freeze_ground_truth")


def main() -> None:
    """Imperative Shell. Performs pure DI composition and triggers the cryptographic sealing use case."""
    base_path = pathlib.Path("tests/corpus/benchmark_v1")

    corpus_loader = LocalFileSystemCorpusLoader(base_path)
    artifact_adapter = LocalFileSystemGroundTruthArtifactAdapter(base_path)

    use_case = SealGroundTruthUseCase(corpus_loader=corpus_loader, artifact_port=artifact_adapter)

    logger.info("Triggering cryptographic lineage seal execution for curated Ground Truth.")
    try:
        global_manifest_hash = use_case.execute(target_version="v1.0")
        logger.info("Cryptographic lock complete. Manifest verified under global SHA-256: %s", global_manifest_hash)
    except Exception as e:
        logger.critical("Catastrophic lineage sealing breakdown: %s", str(e))


if __name__ == "__main__":
    main()