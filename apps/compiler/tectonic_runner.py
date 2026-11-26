# apps/compiler/tectonic_runner.py
"""
Compilador TeX nativo con aislamiento de I/O.

NADR-09 §5.2 R6: Todo artefacto físico de compilación MUST escribirse
en un espacio efímero y aislado por ejecución.
NADR-09 §5.2 R7: La ejecución del compilador constituye un efecto
lateral aislado. No emite transiciones FSM ni muta entidades del dominio.
NADR-09 §5.2 R9: Nomenclatura veraz — invoca tectonic en el host,
no en Docker.

Reemplaza a DockerRunner (DF-30: nomenclatura engañosa).
"""

from dataclasses import dataclass
from xml.sax.saxutils import escape
import subprocess
import tempfile
import shutil
import os
import logging
import re
from pathlib import Path
from typing import Sequence

from core.compiler.rendering.models import AssetReference
from core.compiler.rendering.image_assets import stage_image_assets

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CachedTectonicResources:
    """Explicit cache-only compilation inputs; font bytes are execution immutable."""
    cache_dir: Path
    fonts: tuple[tuple[str, bytes], ...]

    def __post_init__(self) -> None:
        names = [name for name, _ in self.fonts]
        if (not self.cache_dir.is_absolute() or not names or len(names) != len(set(names))
                or any(re.fullmatch(r"[a-zA-Z0-9_-]+\.otf", name) is None
                       or not isinstance(data, bytes) or not data.startswith(b"OTTO")
                       for name, data in self.fonts)):
            raise ValueError("TECTONIC_INVALID_CACHED_RESOURCES")

    def prepare(self, execution_dir: Path) -> dict[str, str]:
        if not self.cache_dir.is_dir():
            raise ValueError("TECTONIC_CACHE_DIRECTORY_MISSING")
        for name, data in self.fonts:
            with (execution_dir / name).open("xb") as stream:
                stream.write(data)
        conf = execution_dir / "fonts.conf"
        conf.write_text(
            '<?xml version="1.0"?>\n<fontconfig><dir>'
            + escape(str(execution_dir)) + '</dir><cachedir>'
            + escape(str(execution_dir / "fc-cache")) + '</cachedir></fontconfig>\n',
            encoding="utf-8",
        )
        return {
            **os.environ,
            "HOME": str(execution_dir),
            "XDG_CONFIG_HOME": str(execution_dir / "config"),
            "XDG_CACHE_HOME": str(self.cache_dir),
            "TECTONIC_CACHE_DIR": str(self.cache_dir),
            "FONTCONFIG_FILE": str(conf),
            "FONTCONFIG_PATH": str(execution_dir),
        }


class HostTectonicRunner:
    """
    Compilador TeX → PDF en el host con aislamiento de I/O.

    NADR-09 §5.2 R6: La compilación ocurre en espacio efímero.
    El artefacto final se persiste en output_dir (explícito, nunca os.getcwd()).
    NADR-09 §5.2 R7: No emite comandos FSM. No muta entidades del dominio.
    """

    def __init__(self, *, cached_resources: CachedTectonicResources | None = None) -> None:
        self._cached_resources = cached_resources

    def compile(
        self, tex_content: str, output_dir: str, output_filename: str = "output.pdf",
        *, image_assets: Sequence[AssetReference] = (),
    ) -> str:
        """
        Compila TeX a PDF en espacio efímero aislado.

        Args:
            tex_content: Contenido TeX a compilar.
            output_dir: Directorio explícito donde persistir el PDF.
                        Obligatorio. El caller decide el destino.
            output_filename: Nombre del archivo PDF (solo basename).

        Returns:
            Ruta absoluta del PDF persistido.

        Raises:
            Exception: Si tectonic falla o excede el timeout.
            FileNotFoundError: Si output_dir no existe.
        """
        # Normalizar a ruta absoluta para cumplir el contrato de retorno.
        # No decide dónde guardar; solo normaliza la ruta recibida.
        output_dir = os.path.abspath(output_dir)

        # Defensa contra path traversal: solo basename, sin componentes de ruta
        output_filename = os.path.basename(output_filename)

        # ... resto del método sin cambios ...

        # Purga de caracteres de control invisibles
        tex_content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', tex_content)
        tex_content = tex_content.replace("&lt;", "<").replace("&gt;", ">")

        # NADR-09 §5.2 R6: Todo el trabajo ocurre en espacio efímero
        with tempfile.TemporaryDirectory() as tmp:
            tex_path = os.path.join(tmp, "doc.tex")

            # Stage verified content-addressed assets in Tectonic's private cwd.
            # The rendered TeX contains only controlled assets/<sha256>.png paths.
            stage_image_assets(
                image_assets,
                source_root=Path(os.getenv("APP_ROOT") or "."),
                execution_dir=Path(tmp),
            )

            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tex_content)

            cmd = ["tectonic", "--untrusted", "doc.tex"]
            env = None
            if self._cached_resources is not None:
                env = self._cached_resources.prepare(Path(tmp))
                cmd.insert(2, "--only-cached")
                logger.info("PPPR_G5_TECTONIC_CACHE_ONLY")

            try:
                if env is None:
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, encoding="utf-8",
                        timeout=120, cwd=tmp,
                    )
                else:
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, encoding="utf-8",
                        timeout=120, cwd=tmp, env=env,
                    )
            except subprocess.TimeoutExpired:
                raise Exception("Fallo de Tectonic: Timeout de 120 segundos excedido.")

            if result.returncode != 0:
                # NADR-09 §5.2 R6: NO escribir en os.getcwd().
                # El stderr se loguea estructuralmente (indexable).
                logger.error("=== TECTONIC FATAL STDERR ===")
                logger.error(result.stderr)
                logger.error("===============================")
                raise Exception(
                    f"Fallo de Tectonic (Exit {result.returncode}). "
                    f"Lee el STDERR en la consola."
                )

            if self._cached_resources is not None and result.stderr:
                logger.warning("PPPR_G5_TECTONIC_STDERR: %s", result.stderr)
            compiled_pdf_path = os.path.join(tmp, "doc.pdf")

            # NADR-09 §5.2 R6: El artefacto se persiste en output_dir
            # explícito. Si no existe, FileNotFoundError (fail-fast).
            # La preparación del directorio pertenece al caller.
            final_path = os.path.join(output_dir, output_filename)
            shutil.copy(compiled_pdf_path, final_path)

            return final_path