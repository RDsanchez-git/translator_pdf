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

import subprocess
import tempfile
import shutil
import os
import logging
import re

logger = logging.getLogger(__name__)


class HostTectonicRunner:
    """
    Compilador TeX → PDF en el host con aislamiento de I/O.

    NADR-09 §5.2 R6: La compilación ocurre en espacio efímero.
    El artefacto final se persiste en output_dir (explícito, nunca os.getcwd()).
    NADR-09 §5.2 R7: No emite comandos FSM. No muta entidades del dominio.
    """

    def compile(self, tex_content: str, output_dir: str, output_filename: str = "output.pdf") -> str:
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

            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tex_content)

            cmd = ["tectonic", "--untrusted", "doc.tex"]

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=120,
                    cwd=tmp
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

            compiled_pdf_path = os.path.join(tmp, "doc.pdf")

            # NADR-09 §5.2 R6: El artefacto se persiste en output_dir
            # explícito. Si no existe, FileNotFoundError (fail-fast).
            # La preparación del directorio pertenece al caller.
            final_path = os.path.join(output_dir, output_filename)
            shutil.copy(compiled_pdf_path, final_path)

            return final_path