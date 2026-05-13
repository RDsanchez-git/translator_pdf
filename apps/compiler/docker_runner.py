import subprocess
import tempfile
import shutil
import os
import logging
import re

logger = logging.getLogger(__name__)

class DockerRunner:
    def compile(self, tex_content: str, output_filename: str = "output.pdf"):
        # SOTA: Purga de caracteres de control invisibles (ej. \x02) que corrompen el tipógrafo
        tex_content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', tex_content)
        
        # SOTA: Purga de artefactos HTML residuales que inyectan '&' fatal no escapado
        tex_content = tex_content.replace("&lt;", "<").replace("&gt;", ">")
        
        with tempfile.TemporaryDirectory() as tmp:
            tex_path = os.path.join(tmp, "doc.tex")
            
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tex_content)

            cmd = [
                "docker", "run", "--rm",
                "-v", f"{tmp}:/usr/src/app",
                "-w", "/usr/src/app",
                "dxjoke/tectonic-docker",
                "tectonic", "doc.tex"
            ]

            try:
                # SOTA: Forzar utf-8 en el I/O del subproceso para evitar el colapso de cp1252 en Windows
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    encoding="utf-8", 
                    timeout=120
                )
            except subprocess.TimeoutExpired:
                raise Exception("Fallo de Tectonic: Timeout de 120 segundos excedido.")

            if result.returncode != 0:
                crash_log_path = os.path.join(os.getcwd(), "tectonic_crash.log")
                with open(crash_log_path, "w", encoding="utf-8") as f:
                    f.write("=== TEX GENERADO ===\n")
                    f.write(tex_content)
                    f.write("\n\n=== TECTONIC STDOUT ===\n")
                    f.write(result.stdout)
                    f.write("\n\n=== TECTONIC STDERR ===\n")
                    f.write(result.stderr)
                    
                logger.error(f"Error en Tectonic. Volcado guardado en: {crash_log_path}")
                raise Exception("Fallo de Tectonic. Revisa tectonic_crash.log para la traza exacta.")

            compiled_pdf_path = os.path.join(tmp, "doc.pdf")
            final_path = os.path.join(os.getcwd(), output_filename)
            shutil.copy(compiled_pdf_path, final_path)

            return final_path