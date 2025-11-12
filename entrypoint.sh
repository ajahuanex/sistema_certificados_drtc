#!/bin/bash
set -e

# Esperar a que la base de datos esté disponible
echo "Esperando a que PostgreSQL esté disponible..."
while ! pg_isready -h ${DB_HOST:-db} -p ${DB_PORT:-5432} -U ${DB_USER:-certificados_user}; do
    echo "PostgreSQL no está listo - esperando..."
    sleep 2
done
echo "PostgreSQL está disponible!"

# Ejecutar migraciones
echo "Ejecutando migraciones..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Crear superusuario si no existe (o actualizar si existe)
echo "Verificando superusuario..."
python manage.py create_superuser_if_not_exists --update --noinput

# Cargar plantilla por defecto si no existe
echo "Cargando plantilla por defecto..."
python manage.py load_default_template

echo "Iniciando aplicación..."
exec "$@"
