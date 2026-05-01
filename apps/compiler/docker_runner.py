import subprocess
import tempfile
import shutil
import os

class DockerRunner:
    def compile(self, tex_content: str, output_filename: str = "output.pdf"):
        with tempfile.TemporaryDirectory() as tmp:
            tex_path = os.path.join(tmp, "doc.tex")
            
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tex_content)

            # SOTA: Uso real de contenedor efímero mapeando el volumen temporal
            cmd = [
                "docker", "run", "--rm",
                "-v", f"{tmp}:/usr/src/app",
                "-w", "/usr/src/app",
                "dxjoke/tectonic-docker",
                "tectonic", "doc.tex"
            ]

            result = subprocess.run(cmd, capture_output=True)

            if result.returncode != 0:
                raise Exception(f"Fallo de Tectonic:\n{result.stderr.decode()}")

            # Persistir el artefacto antes de que el context manager destruya 'tmp'
            compiled_pdf_path = os.path.join(tmp, "doc.pdf")
            final_path = os.path.join(os.getcwd(), output_filename)
            shutil.copy(compiled_pdf_path, final_path)

            return final_path