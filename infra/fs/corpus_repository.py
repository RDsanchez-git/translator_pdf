import json
import os
import pathlib
import tempfile

from core.benchmark.corpus.dtos import RawCorpusManifestDTO
from core.benchmark.corpus.ports import (
    CorpusManifestReaderPort,
    CorpusManifestWriterPort,
)


class LocalFileSystemCorpusLoader(CorpusManifestReaderPort, CorpusManifestWriterPort):
    """Adaptador físico del manifiesto del corpus.

    Implementa ambos puertos segregados (NADR-14 §5.1 R1). Un único
    adaptador puede implementar múltiples puertos cuando operan sobre el
    mismo recurso subyacente.
    """

    def __init__(self, base_path: pathlib.Path):
        self.base_path = pathlib.Path(base_path)
        if self.base_path.is_file() or self.base_path.suffix == ".json":
            self.manifest_file = self.base_path
        else:
            self.manifest_file = self.base_path / "manifest.json"

    def load_raw_manifest(self) -> RawCorpusManifestDTO:
        """Lectura runtime. Fail-fast si el manifiesto no existe (E-2.0-05).

        NADR-14 §5.3 R8: los fallos de integridad se propagan como errores
        explícitos, sin degradación a advertencias (Cero Fallos Silenciosos).
        """
        if not self.manifest_file.exists():
            raise FileNotFoundError(
                f"Manifest not found: {self.manifest_file}. "
                f"Create the manifest before running reconciliation."
            )
        with open(self.manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return RawCorpusManifestDTO.model_validate(data)

    def save_manifest_dto(self, dto: RawCorpusManifestDTO) -> None:
        """Escritura de curaduría. Atómica con tempfile + fsync + os.replace (E-2.0-06).

        Coherente con write_ast_json_atomic (NADR-F17BIS-01 §5.6) y la
        corrección DF-15 (os.replace multiplataforma).
        """
        self.manifest_file.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(dto.model_dump(), indent=2, ensure_ascii=False)

        with tempfile.NamedTemporaryFile(
            "w", dir=self.manifest_file.parent, delete=False, encoding="utf-8"
        ) as tf:
            temp_path = pathlib.Path(tf.name)
            tf.write(content)
            tf.flush()
            try:
                os.fsync(tf.fileno())
            except (AttributeError, OSError):
                pass

        os.replace(temp_path, self.manifest_file)