import json
import pathlib
from core.benchmark.corpus.ports import CorpusManifestLoaderPort
from core.benchmark.corpus.dtos import RawCorpusManifestDTO

class LocalFileSystemCorpusLoader(CorpusManifestLoaderPort):
    def __init__(self, base_path: pathlib.Path):
        self.manifest_file = base_path / "manifest.json"

    def load_raw_manifest(self) -> RawCorpusManifestDTO:
        if not self.manifest_file.exists():
            raise FileNotFoundError(f"Manifiesto ausente en {self.manifest_file}")
        with open(self.manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return RawCorpusManifestDTO.model_validate(data)

    def save_manifest_dto(self, dto: RawCorpusManifestDTO) -> None:
        with open(self.manifest_file, "w", encoding="utf-8") as f:
            json.dump(dto.model_dump(), f, indent=2, ensure_ascii=False)