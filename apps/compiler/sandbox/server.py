from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import tempfile
import os
import time

app = FastAPI()

class CompileRequest(BaseModel):
    chunk_id: str
    latex_content: str

class CompileResult(BaseModel):
    chunk_id: str
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    compile_time_ms: float

# SOTA: Plantilla mínima y estéril para probar sintaxis aislada
TEX_TEMPLATE = r"""\documentclass{article}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\begin{document}
% --- BEGIN CHUNK ---
<CHUNK_CONTENT>
% --- END CHUNK ---
\end{document}
"""

@app.post("/compile", response_model=CompileResult)
async def compile_chunk(request: CompileRequest):
    start_time = time.perf_counter()
    
    # SOTA: Inyectar el fragmento en un entorno aislado y seguro
    full_tex = TEX_TEMPLATE.replace("<CHUNK_CONTENT>", request.latex_content)
    
    # SOTA: Usamos NamedTemporaryFile en RAM (tmpfs) si el contenedor está bien configurado
    with tempfile.NamedTemporaryFile(suffix=".tex", delete=False, mode="w", encoding="utf-8") as temp_tex:
        temp_tex.write(full_tex)
        temp_path = temp_tex.name

    try:
        # Ejecución SOTA: timeout agresivo para evitar deadlocks infinitos de compiladores
        result = subprocess.run(
            ["tectonic", temp_path],
            capture_output=True,
            text=True,
            timeout=5.0 
        )
        
        success = (result.returncode == 0)
        
        return CompileResult(
            chunk_id=request.chunk_id,
            success=success,
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            compile_time_ms=(time.perf_counter() - start_time) * 1000
        )
        
    except subprocess.TimeoutExpired as e:
        return CompileResult(
            chunk_id=request.chunk_id,
            success=False,
            exit_code=-1,
            stdout=str(e.stdout) if hasattr(e, 'stdout') else "",
            stderr="Timeout de compilación (posible loop infinito en entorno anidado).",
            compile_time_ms=(time.perf_counter() - start_time) * 1000
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)