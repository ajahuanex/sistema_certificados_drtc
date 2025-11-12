# Dockerfile para Sistema de Certificados DRTC
# Multi-stage build para optimizar tamaño de imagen

# Etapa 1: Builder - Instalar dependencias y compilar
FROM python:3.11-slim as builder

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema necesarias para compilación
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    zlib1g-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# Etapa 2: Runtime - Imagen final optimizada
FROM python:3.11-slim as runtime

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/app/.local/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.production

# Instalar dependencias runtime necesarias
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gettext \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash app

# Configurar directorio de trabajo
WORKDIR /app

# Copiar dependencias Python desde builder
COPY --from=builder /root/.local /home/app/.local

# Crear directorios necesarios
RUN mkdir -p /app/media /app/staticfiles /app/logs \
    && chown -R app:app /app

# Copiar script de entrada primero (como root para dar permisos)
COPY entrypoint.sh /app/entrypoint.sh

# Dar permisos de ejecución al entrypoint
RUN chmod +x /app/entrypoint.sh && chown app:app /app/entrypoint.sh

# Cambiar a usuario no-root
USER app

# Copiar código de la aplicación
COPY --chown=app:app . .

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Punto de entrada y comando por defecto
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "300", "config.wsgi:application"]