import json
import pathlib
from core.benchmark.corpus.dtos import RawCorpusManifestDTO
from core.benchmark.corpus.ports import CorpusManifestLoaderPort


class LocalFileSystemCorpusLoader(CorpusManifestLoaderPort):
    def __init__(self, base_path: pathlib.Path):
        self.base_path = pathlib.Path(base_path)
        # Normaliza la ruta si se inyecta el directorio base o el archivo directo
        if self.base_path.is_file() or self.base_path.suffix == ".json":
            self.manifest_file = self.base_path
        else:
            self.manifest_file = self.base_path / "manifest.json"

    def load_raw_manifest(self) -> RawCorpusManifestDTO:
        if not self.manifest_file.exists():
            return RawCorpusManifestDTO(
                corpus_version="v1.0",
                manifest_hash="",
                documents=[]
            )

        with open(self.manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return RawCorpusManifestDTO.model_validate(data)

    def save_manifest_dto(self, dto: RawCorpusManifestDTO) -> None:
        self.manifest_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_file, "w", encoding="utf-8") as f:
            json.dump(dto.model_dump(), f, indent=2, ensure_ascii=False)