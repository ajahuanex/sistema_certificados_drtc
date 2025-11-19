#!/bin/bash

# Script para actualizar el código en producción
# Ejecutar en el servidor de producción

echo "========================================="
echo "ACTUALIZANDO SISTEMA EN PRODUCCIÓN"
echo "========================================="
echo ""

# Ir al directorio del proyecto
cd /home/administrador/dockers/sistema_certificados_drtc

# Hacer backup de la base de datos
echo "1. Creando backup de la base de datos..."
docker compose exec -T db pg_dump -U certificados_user certificados_prod > backup_$(date +%Y%m%d_%H%M%S).sql
echo "✓ Backup creado"
echo ""

# Actualizar código desde GitHub
echo "2. Actualizando código desde GitHub..."
git pull origin main
echo "✓ Código actualizado"
echo ""

# Recolectar archivos estáticos
echo "3. Recolectando archivos estáticos..."
docker compose exec -T web python manage.py collectstatic --noinput
echo "✓ Archivos estáticos recolectados"
echo ""

# Aplicar migraciones
echo "4. Aplicando migraciones de base de datos..."
docker compose exec -T web python manage.py migrate --noinput
echo "✓ Migraciones aplicadas"
echo ""

# Reiniciar contenedores
echo "5. Reiniciando contenedores..."
docker compose restart web
echo "✓ Contenedores reiniciados"
echo ""

# Esperar a que el servicio esté listo
echo "6. Esperando a que el servicio esté listo..."
sleep 10
echo ""

# Verificar estado
echo "7. Verificando estado del servicio..."
docker compose ps
echo ""

# Mostrar logs recientes
echo "8. Logs recientes:"
docker compose logs --tail=20 web
echo ""

echo "========================================="
echo "ACTUALIZACIÓN COMPLETADA"
echo "========================================="
echo ""
echo "Verificar en: https://certificados.transportespuno.gob.pe/"
echo ""
