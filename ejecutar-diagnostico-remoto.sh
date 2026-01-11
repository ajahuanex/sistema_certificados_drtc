#!/bin/bash

# Script para ejecutar diagnóstico en servidor remoto
IP_SERVIDOR=${1:-"161.132.47.92"}
USUARIO="administrador"
DIRECTORIO="~/dockers/sistema_certificados_drtc"

echo "=== EJECUTANDO DIAGNÓSTICO EN SERVIDOR REMOTO ==="
echo "Servidor: $IP_SERVIDOR"
echo "Usuario: $USUARIO"
echo "Directorio: $DIRECTORIO"
echo ""

# Crear el script de diagnóstico en el servidor remoto y ejecutarlo
ssh -t $USUARIO@$IP_SERVIDOR << ENDSSH
cd $DIRECTORIO

echo "=========================================="
echo "DIAGNÓSTICO PASO A PASO - SERVIDOR REMOTO"
echo "=========================================="
echo ""

echo "=== PASO 1: INFORMACIÓN BÁSICA ==="
echo "Fecha: \$(date)"
echo "Usuario: \$(whoami)"
echo "Directorio: \$(pwd)"
echo "Espacio en disco:"
df -h | head -5
echo ""

echo "=== PASO 2: ARCHIVOS DEL PROYECTO ==="
echo "Archivos principales:"
ls -la | grep -E "(docker-compose|\.env|Dockerfile)"
echo ""

echo "=== PASO 3: CONFIGURACIÓN REDIS ACTUAL ==="
echo "En .env.production:"
if [ -f ".env.production" ]; then
    grep -n "REDIS" .env.production
else
    echo "❌ .env.production no existe"
fi
echo ""

echo "En docker-compose.prod.yml:"
if [ -f "docker-compose.prod.yml" ]; then
    echo "Sección redis (líneas relevantes):"
    grep -A 10 -B 2 "redis:" docker-compose.prod.yml | head -15
else
    echo "❌ docker-compose.prod.yml no existe"
fi
echo ""

echo "=== PASO 4: ESTADO DOCKER ==="
echo "Versión Docker: \$(docker --version)"
echo "Versión Docker Compose: \$(docker compose version)"
echo ""

echo "Contenedores ejecutándose:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "=== PASO 5: SERVICIOS DEL PROYECTO ==="
if [ -f "docker-compose.prod.yml" ]; then
    echo "Estado servicios:"
    docker compose -f docker-compose.prod.yml ps
else
    echo "❌ No se puede verificar - archivo no existe"
fi
echo ""

echo "=== PASO 6: LOGS RECIENTES ==="
if [ -f "docker-compose.prod.yml" ]; then
    echo "Logs WEB (últimas 5 líneas):"
    docker compose -f docker-compose.prod.yml logs web --tail=5 2>/dev/null || echo "Servicio web no disponible"
    echo ""
    
    echo "Logs REDIS (últimas 5 líneas):"
    docker compose -f docker-compose.prod.yml logs redis --tail=5 2>/dev/null || echo "Servicio redis no disponible"
    echo ""
fi

echo "=== PASO 7: PRUEBAS DE CONECTIVIDAD ==="
echo "Puerto 7070:"
curl -I http://localhost:7070 2>/dev/null | head -1 || echo "❌ Puerto 7070 no responde"

echo ""
echo "Redis sin contraseña:"
docker compose -f docker-compose.prod.yml exec redis redis-cli ping 2>/dev/null || echo "❌ Redis sin contraseña no responde"

echo ""
echo "Redis con contraseña:"
docker compose -f docker-compose.prod.yml exec redis redis-cli -a redis_password ping 2>/dev/null || echo "❌ Redis con contraseña no responde"

echo ""
echo "PostgreSQL:"
docker compose -f docker-compose.prod.yml exec db pg_isready -U certificados_user -d certificados_prod 2>/dev/null || echo "❌ PostgreSQL no responde"

echo ""
echo "=== PASO 8: ANÁLISIS DE ERRORES ==="
echo "Errores de autenticación Redis (últimas 3):"
docker compose -f docker-compose.prod.yml logs web 2>/dev/null | grep -i "authentication" | tail -3 || echo "No se encontraron errores de autenticación"

echo ""
echo "Errores de conexión (últimas 3):"
docker compose -f docker-compose.prod.yml logs web 2>/dev/null | grep -i "connection.*error\|connection.*failed" | tail -3 || echo "No se encontraron errores de conexión"

echo ""
echo "=== PASO 9: VOLÚMENES Y REDES ==="
echo "Volúmenes del proyecto:"
docker volume ls | grep -E "(redis|postgres|certificados)" || echo "No se encontraron volúmenes específicos"

echo ""
echo "Redes del proyecto:"
docker network ls | grep certificados || echo "No se encontró red específica"

echo ""
echo "=== DIAGNÓSTICO COMPLETADO ==="
echo ""
echo "PRÓXIMOS PASOS RECOMENDADOS:"
echo "1. Si Redis no responde con contraseña, actualizar configuración"
echo "2. Si hay errores de autenticación, corregir REDIS_URL"
echo "3. Si servicios no están ejecutándose, reiniciar con docker compose up -d"
echo ""
echo "¿Deseas continuar con la corrección automática? (s/n)"

ENDSSH

echo ""
echo "=== DIAGNÓSTICO REMOTO COMPLETADO ==="
echo ""
echo "Basado en los resultados, ¿quieres que ejecute la corrección automática?"
echo "Ejecuta: ./fix-redis-remoto.sh para aplicar la solución"