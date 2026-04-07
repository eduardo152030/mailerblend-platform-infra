# --- ETAPA 1: Builder ---
FROM python:3.11-slim AS builder

# Evita que Python genere archivos .pyc y asegura salida de logs inmediata
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Solo instalamos herramientas de compilación necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Instalamos dependencias en un directorio de usuario para facilitar la copia
RUN pip install --user --no-cache-dir -r requirements.txt


# --- ETAPA 2: Final (Producción) ---
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Aseguramos que los binarios instalados en la etapa anterior sean visibles
    PATH="/home/appuser/.local/bin:${PATH}"

# Instalamos solo librerías de ejecución (como libpq para postgres) y utilidades de red
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Creamos un usuario no-root por seguridad
RUN useradd -m appuser
USER appuser

# Copiamos solo las dependencias instaladas desde el builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
# Copiamos el código fuente con los permisos correctos
COPY --chown=appuser:appuser . .

# El puerto se puede sobreescribir en el compose si es necesario
EXPOSE 8000

# Usamos ENTRYPOINT para permitir pasar argumentos extra fácilmente
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]