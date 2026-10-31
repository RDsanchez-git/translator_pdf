FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 1. Dependencias del Sistema: Instalar curl y dependencias nativas para Tectonic
RUN apt-get update && apt-get install -y \
    curl \
    fontconfig \
    libfontconfig1 \
    libgraphite2-3 \
    libharfbuzz0b \
    libharfbuzz-icu0 \
    libfreetype6 \
    libpng16-16 \
    && rm -rf /var/lib/apt/lists/*

# 2. SOTA: Descargar e instalar Tectonic binario inmutable desde GitHub Releases (Bypass DNS)
RUN curl -sSL -o tectonic.tar.gz https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.15.0/tectonic-0.15.0-x86_64-unknown-linux-gnu.tar.gz \
    && tar -xzf tectonic.tar.gz \
    && mv tectonic /usr/local/bin/ \
    && rm tectonic.tar.gz

WORKDIR /app

# 3. Instalacion del proyecto desde pyproject.toml
COPY . /app/
RUN python -m pip install --default-timeout=1000 --no-cache-dir .

CMD ["python", "runtime/engine.py"]