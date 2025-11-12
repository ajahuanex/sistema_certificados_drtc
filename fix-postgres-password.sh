#!/bin/bash

# Script para solucionar el problema de autenticación de PostgreSQL
# Sistema de Certificados DRTC

echo "=========================================="
echo "🔧 Solucionando problema de PostgreSQL"
echo "=========================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}⚠️  ADVERTENCIA: Esta operación recreará la base de datos${NC}"
echo -e "${YELLOW}   Se perderán todos los datos existentes.${NC}"
echo ""
read -p "¿Deseas continuar? (s/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${RED}❌ Operación cancelada${NC}"
    exit 1
fi

echo ""
echo "Paso 1: Deteniendo servicios..."
docker compose -f docker-compose.prod.yml --env-file .env.production down

echo ""
echo "Paso 2: Eliminando volumen de PostgreSQL..."
docker volume rm sistema_certificados_drtc_postgres_data_prod 2>/dev/null || echo "Volumen no existe o ya fue eliminado"

echo ""
echo "Paso 3: Levantando servicios..."
docker compose -f docker-compose.prod.yml --env-file .env.production up -d

echo ""
echo "Paso 4: Esperando que los servicios estén listos (30 segundos)..."
sleep 30

echo ""
echo "Paso 5: Verificando estado de servicios..."
docker compose -f docker-compose.prod.yml --env-file .env.production ps

echo ""
echo "Paso 6: Ejecutando migraciones..."
docker compose -f docker-compose.prod.yml --env-file .env.production exec -T web python manage.py migrate

echo ""
echo "Paso 7: Creando superusuario..."
docker compose -f docker-compose.prod.yml --env-file .env.production exec -T web python manage.py create_superuser_if_not_exists

echo ""
echo "Paso 8: Cargando plantilla por defecto..."
docker compose -f docker-compose.prod.yml --env-file .env.production exec -T web python manage.py load_default_template

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Proceso completado${NC}"
echo "=========================================="
echo ""
echo "Verificación final:"
echo ""
echo "1. Estado de servicios:"
docker compose -f docker-compose.prod.yml --env-file .env.production ps
echo ""
echo "2. Últimos logs del servicio web:"
docker compose -f docker-compose.prod.yml --env-file .env.production logs web --tail 20
echo ""
echo "=========================================="
echo "Accede a la aplicación en:"
echo "  http://localhost:7070"
echo ""
echo "Credenciales de administrador:"
echo "  Usuario: admin"
echo "  Contraseña: admin123"
echo "=========================================="
