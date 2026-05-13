# SOTA: Base ligera de Python (requerida para FastAPI)
FROM python:3.11-slim

# Instalar dependencias del sistema y el binario SOTA de Tectonic
RUN apt-get update && apt-get install -y \
    curl \
    libfontconfig1 \
    libharfbuzz0b \
    libgraphite2-3 \
    && curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh \
    && mv tectonic /usr/local/bin/ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias para el Sandbox en memoria
RUN pip install --no-cache-dir fastapi uvicorn pydantic

# Copiar el código del Sandbox al contenedor
COPY apps/compiler/sandbox/server.py /app/sandbox_server.py

WORKDIR /app

# Exponer el puerto del microservicio interno
EXPOSE 8000

# Arrancar el Warm Pool persistente
CMD ["uvicorn", "sandbox_server:app", "--host", "0.0.0.0", "--port", "8000"]docker build -t tectonic-sandbox -f infra/docker/texlive.Dockerfile .