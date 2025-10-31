#!/bin/bash
# Script de inicio para el contenedor Docker

set -e

echo "🚀 Iniciando Sistema de Certificados DRTC Puno..."

# Esperar a que la base de datos esté lista
echo "⏳ Esperando a PostgreSQL..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER > /dev/null 2>&1; do
    sleep 1
done
echo "✅ PostgreSQL está listo"

# Ejecutar migraciones
echo "📦 Ejecutando migraciones..."
python manage.py migrate --noinput

# Crear superusuario si no existe
echo "👤 Verificando superusuario..."
python manage.py create_superuser_if_not_exists

# Cargar plantilla por defecto
echo "📄 Cargando plantilla por defecto..."
python manage.py load_default_template || true

# Cargar configuración de QR
echo "🔧 Cargando configuración de QR..."
python manage.py load_qr_config || true

# Recolectar archivos estáticos
echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "✅ Inicialización completada"
echo "🌐 Servidor listo en http://0.0.0.0:8000"

# Ejecutar el comando pasado como argumento
exec "$@"
