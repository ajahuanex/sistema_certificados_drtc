#!/bin/bash

# ============================================
# Script de Verificación y Despliegue Automático
# Sistema de Certificados DRTC
# ============================================

set -e  # Detener en caso de error

echo "============================================"
echo "VERIFICACIÓN Y DESPLIEGUE AUTOMÁTICO"
echo "Sistema de Certificados DRTC"
echo "============================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================
# PASO 1: Verificar puertos
# ============================================
echo "📋 PASO 1: Verificando puertos..."
echo ""

PUERTOS_OCUPADOS=0

# Verificar puerto 7070 (nginx externo)
if lsof -Pi :7070 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Puerto 7070 está ocupado${NC}"
    echo "Procesos usando el puerto 7070:"
    lsof -Pi :7070 -sTCP:LISTEN
    PUERTOS_OCUPADOS=1
else
    echo -e "${GREEN}✅ Puerto 7070 está libre${NC}"
fi

# Verificar puerto 5433 (PostgreSQL)
if lsof -Pi :5433 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Puerto 5433 está ocupado${NC}"
    echo "Procesos usando el puerto 5433:"
    lsof -Pi :5433 -sTCP:LISTEN
    PUERTOS_OCUPADOS=1
else
    echo -e "${GREEN}✅ Puerto 5433 está libre${NC}"
fi

# Verificar puerto 6380 (Redis)
if lsof -Pi :6380 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Puerto 6380 está ocupado${NC}"
    echo "Procesos usando el puerto 6380:"
    lsof -Pi :6380 -sTCP:LISTEN
    PUERTOS_OCUPADOS=1
else
    echo -e "${GREEN}✅ Puerto 6380 está libre${NC}"
fi

echo ""

# Si hay puertos ocupados, preguntar si continuar
if [ $PUERTOS_OCUPADOS -eq 1 ]; then
    echo -e "${YELLOW}⚠️  Algunos puertos están ocupados${NC}"
    echo ""
    echo "Opciones:"
    echo "1. Detener contenedores existentes y continuar"
    echo "2. Cancelar despliegue"
    echo ""
    read -p "Selecciona una opción (1/2): " OPCION
    
    if [ "$OPCION" = "1" ]; then
        echo ""
        echo "🛑 Deteniendo contenedores existentes..."
        docker compose -f docker-compose.prod.yml --env-file .env.production down 2>/dev/null || true
        echo -e "${GREEN}✅ Contenedores detenidos${NC}"
        echo ""
    else
        echo -e "${RED}❌ Despliegue cancelado${NC}"
        exit 1
    fi
fi

# ============================================
# PASO 2: Verificar archivos necesarios
# ============================================
echo "📋 PASO 2: Verificando archivos necesarios..."
echo ""

ARCHIVOS_FALTANTES=0

if [ ! -f ".env.production" ]; then
    echo -e "${RED}❌ Falta archivo: .env.production${NC}"
    ARCHIVOS_FALTANTES=1
else
    echo -e "${GREEN}✅ .env.production encontrado${NC}"
fi

if [ ! -f "docker-compose.prod.yml" ]; then
    echo -e "${RED}❌ Falta archivo: docker-compose.prod.yml${NC}"
    ARCHIVOS_FALTANTES=1
else
    echo -e "${GREEN}✅ docker-compose.prod.yml encontrado${NC}"
fi

if [ ! -f "nginx.prod.http-only.conf" ]; then
    echo -e "${RED}❌ Falta archivo: nginx.prod.http-only.conf${NC}"
    ARCHIVOS_FALTANTES=1
else
    echo -e "${GREEN}✅ nginx.prod.http-only.conf encontrado${NC}"
fi

if [ ! -f "entrypoint.sh" ]; then
    echo -e "${RED}❌ Falta archivo: entrypoint.sh${NC}"
    ARCHIVOS_FALTANTES=1
else
    echo -e "${GREEN}✅ entrypoint.sh encontrado${NC}"
fi

if [ $ARCHIVOS_FALTANTES -eq 1 ]; then
    echo ""
    echo -e "${RED}❌ Faltan archivos necesarios. Ejecuta 'git pull' primero.${NC}"
    exit 1
fi

echo ""

# ============================================
# PASO 3: Dar permisos a entrypoint.sh
# ============================================
echo "📋 PASO 3: Configurando permisos..."
echo ""

chmod +x entrypoint.sh
echo -e "${GREEN}✅ Permisos de ejecución dados a entrypoint.sh${NC}"
echo ""

# ============================================
# PASO 4: Hacer backup de .env
# ============================================
echo "📋 PASO 4: Haciendo backup de configuración..."
echo ""

BACKUP_FILE=".env.production.backup.$(date +%Y%m%d_%H%M%S)"
cp .env.production "$BACKUP_FILE"
echo -e "${GREEN}✅ Backup creado: $BACKUP_FILE${NC}"
echo ""

# ============================================
# PASO 5: Construir imágenes
# ============================================
echo "📋 PASO 5: Construyendo imágenes Docker..."
echo ""

docker compose -f docker-compose.prod.yml --env-file .env.production build --no-cache web
echo -e "${GREEN}✅ Imagen web construida${NC}"
echo ""

# ============================================
# PASO 6: Levantar servicios
# ============================================
echo "📋 PASO 6: Levantando servicios..."
echo ""

docker compose -f docker-compose.prod.yml --env-file .env.production up -d
echo -e "${GREEN}✅ Servicios levantados${NC}"
echo ""

# ============================================
# PASO 7: Esperar a que inicien
# ============================================
echo "📋 PASO 7: Esperando a que los servicios inicien..."
echo ""

echo "Esperando 30 segundos..."
for i in {30..1}; do
    echo -ne "⏳ $i segundos restantes...\r"
    sleep 1
done
echo -e "${GREEN}✅ Servicios iniciados${NC}"
echo ""

# ============================================
# PASO 8: Verificar estado de contenedores
# ============================================
echo "📋 PASO 8: Verificando estado de contenedores..."
echo ""

docker compose -f docker-compose.prod.yml --env-file .env.production ps
echo ""

# ============================================
# PASO 9: Configurar nginx
# ============================================
echo "📋 PASO 9: Configurando nginx..."
echo ""

# Obtener nombre del contenedor nginx
NGINX_CONTAINER=$(docker ps --filter "name=nginx" --format "{{.Names}}" | head -n 1)

if [ -z "$NGINX_CONTAINER" ]; then
    echo -e "${RED}❌ No se encontró contenedor nginx${NC}"
    exit 1
fi

echo "Contenedor nginx: $NGINX_CONTAINER"

# Copiar configuración
docker cp nginx.prod.http-only.conf "$NGINX_CONTAINER:/etc/nginx/nginx.conf"
echo -e "${GREEN}✅ Configuración nginx copiada${NC}"

# Verificar configuración
docker compose -f docker-compose.prod.yml --env-file .env.production exec nginx nginx -t
echo -e "${GREEN}✅ Configuración nginx válida${NC}"
echo ""

# ============================================
# PASO 10: Recolectar archivos estáticos
# ============================================
echo "📋 PASO 10: Recolectando archivos estáticos..."
echo ""

docker compose -f docker-compose.prod.yml --env-file .env.production exec web python manage.py collectstatic --noinput --clear
echo -e "${GREEN}✅ Archivos estáticos recolectados${NC}"
echo ""

# ============================================
# PASO 11: Recargar nginx
# ============================================
echo "📋 PASO 11: Recargando nginx..."
echo ""

docker compose -f docker-compose.prod.yml --env-file .env.production exec nginx nginx -s reload
echo -e "${GREEN}✅ Nginx recargado${NC}"
echo ""

# ============================================
# PASO 12: Verificación final
# ============================================
echo "📋 PASO 12: Verificación final..."
echo ""

# Verificar archivos estáticos
echo "Verificando archivos estáticos..."
docker compose -f docker-compose.prod.yml --env-file .env.production exec web ls -la /app/staticfiles/admin/css/ | head -n 5
echo ""

# Verificar logs
echo "Últimos logs de web:"
docker compose -f docker-compose.prod.yml --env-file .env.production logs --tail=10 web
echo ""

echo "Últimos logs de nginx:"
docker compose -f docker-compose.prod.yml --env-file .env.production logs --tail=10 nginx
echo ""

# ============================================
# RESUMEN FINAL
# ============================================
echo "============================================"
echo -e "${GREEN}✅ DESPLIEGUE COMPLETADO EXITOSAMENTE${NC}"
echo "============================================"
echo ""
echo "🌐 Acceso a la aplicación:"
echo "   URL: http://161.132.47.92:7070/admin/"
echo "   Usuario: admin"
echo "   Contraseña: admin123"
echo ""
echo "📊 Comandos útiles:"
echo "   Ver logs: docker compose -f docker-compose.prod.yml --env-file .env.production logs -f"
echo "   Ver estado: docker compose -f docker-compose.prod.yml --env-file .env.production ps"
echo "   Reiniciar: docker compose -f docker-compose.prod.yml --env-file .env.production restart"
echo ""
echo "📁 Backup creado: $BACKUP_FILE"
echo ""
echo "🎉 ¡Listo para usar!"
echo ""
