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

            # SOTA: Invocación nativa, eliminando el wrapper de Docker.
            cmd = ["tectonic", "--untrusted", "doc.tex"]

            try:
                # SOTA: Forzar utf-8 en el I/O del subproceso.
                # Inyectamos cwd=tmp para que los artefactos se generen en el directorio efímero.
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
                # SOTA: Bypass del File System. Log directo a stdout de Docker.
                logger.error("=== TECTONIC FATAL STDERR ===")
                logger.error(result.stderr)
                logger.error("===============================")
                
                # Opcional: mantén el volcado a disco si quieres, pero ya no dependemos de él.
                crash_log_path = os.path.join(os.getcwd(), "tectonic_crash.log")
                with open(crash_log_path, "w", encoding="utf-8") as f:
                    f.write(result.stderr)
                    
                raise Exception(f"Fallo de Tectonic (Exit {result.returncode}). Lee el STDERR en la consola.")

            compiled_pdf_path = os.path.join(tmp, "doc.pdf")
            final_path = os.path.join(os.getcwd(), output_filename)
            shutil.copy(compiled_pdf_path, final_path)

            return final_path