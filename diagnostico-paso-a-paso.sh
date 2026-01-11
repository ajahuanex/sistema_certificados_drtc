#!/bin/bash

echo "=========================================="
echo "DIAGNÓSTICO PASO A PASO - SERVIDOR REMOTO"
echo "=========================================="
echo ""

# Colores para mejor visualización
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== PASO 1: INFORMACIÓN DEL SISTEMA ===${NC}"
echo "Fecha y hora actual:"
date
echo ""
echo "Usuario actual:"
whoami
echo ""
echo "Directorio actual:"
pwd
echo ""
echo "Espacio en disco:"
df -h
echo ""

echo -e "${BLUE}=== PASO 2: VERIFICAR ARCHIVOS DEL PROYECTO ===${NC}"
echo "Archivos principales del proyecto:"
ls -la | grep -E "(docker-compose|\.env|Dockerfile)"
echo ""

if [ -f "docker-compose.prod.yml" ]; then
    echo -e "${GREEN}✓ docker-compose.prod.yml existe${NC}"
else
    echo -e "${RED}✗ docker-compose.prod.yml NO existe${NC}"
fi

if [ -f ".env.production" ]; then
    echo -e "${GREEN}✓ .env.production existe${NC}"
else
    echo -e "${RED}✗ .env.production NO existe${NC}"
fi
echo ""

echo -e "${BLUE}=== PASO 3: CONFIGURACIÓN ACTUAL DE REDIS ===${NC}"
echo "Configuración Redis en .env.production:"
if [ -f ".env.production" ]; then
    grep -n "REDIS" .env.production || echo "No se encontraron configuraciones REDIS"
else
    echo -e "${RED}Archivo .env.production no existe${NC}"
fi
echo ""

echo "Configuración Redis en docker-compose.prod.yml:"
if [ -f "docker-compose.prod.yml" ]; then
    echo "Sección redis:"
    sed -n '/redis:/,/healthcheck:/p' docker-compose.prod.yml
else
    echo -e "${RED}Archivo docker-compose.prod.yml no existe${NC}"
fi
echo ""

echo -e "${BLUE}=== PASO 4: ESTADO DE DOCKER ===${NC}"
echo "Versión de Docker:"
docker --version
echo ""
echo "Versión de Docker Compose:"
docker compose version
echo ""

echo "Contenedores en ejecución:"
docker ps
echo ""

echo "Todos los contenedores (incluyendo detenidos):"
docker ps -a
echo ""

echo -e "${BLUE}=== PASO 5: ESTADO DE LOS SERVICIOS DEL PROYECTO ===${NC}"
if [ -f "docker-compose.prod.yml" ]; then
    echo "Estado de servicios del proyecto:"
    docker compose -f docker-compose.prod.yml ps
    echo ""
else
    echo -e "${RED}No se puede verificar servicios - docker-compose.prod.yml no existe${NC}"
fi

echo -e "${BLUE}=== PASO 6: VOLÚMENES DE DOCKER ===${NC}"
echo "Volúmenes existentes:"
docker volume ls | grep -E "(redis|postgres|certificados)" || echo "No se encontraron volúmenes relacionados"
echo ""

echo -e "${BLUE}=== PASO 7: REDES DE DOCKER ===${NC}"
echo "Redes existentes:"
docker network ls | grep -E "(certificados|bridge)" || echo "Solo redes por defecto"
echo ""

echo -e "${BLUE}=== PASO 8: LOGS DE LOS SERVICIOS ===${NC}"
if [ -f "docker-compose.prod.yml" ]; then
    echo "Logs del servicio web (últimas 10 líneas):"
    docker compose -f docker-compose.prod.yml logs web --tail=10 2>/dev/null || echo "Servicio web no está ejecutándose"
    echo ""
    
    echo "Logs del servicio redis (últimas 10 líneas):"
    docker compose -f docker-compose.prod.yml logs redis --tail=10 2>/dev/null || echo "Servicio redis no está ejecutándose"
    echo ""
    
    echo "Logs del servicio db (últimas 10 líneas):"
    docker compose -f docker-compose.prod.yml logs db --tail=10 2>/dev/null || echo "Servicio db no está ejecutándose"
    echo ""
fi

echo -e "${BLUE}=== PASO 9: CONECTIVIDAD DE RED ===${NC}"
echo "Puertos en uso:"
netstat -tlnp | grep -E ":7070|:5432|:6379" || echo "Puertos principales no están en uso"
echo ""

echo "Verificar si el puerto 7070 responde:"
curl -I http://localhost:7070 2>/dev/null || echo "Puerto 7070 no responde"
echo ""

echo -e "${BLUE}=== PASO 10: PRUEBAS DE CONECTIVIDAD INTERNA ===${NC}"
if docker compose -f docker-compose.prod.yml ps | grep -q "redis"; then
    echo "Probando conexión a Redis SIN contraseña:"
    docker compose -f docker-compose.prod.yml exec redis redis-cli ping 2>/dev/null || echo "Redis sin contraseña no responde"
    
    echo "Probando conexión a Redis CON contraseña:"
    docker compose -f docker-compose.prod.yml exec redis redis-cli -a redis_password ping 2>/dev/null || echo "Redis con contraseña no responde"
else
    echo "Servicio Redis no está ejecutándose"
fi
echo ""

if docker compose -f docker-compose.prod.yml ps | grep -q "db"; then
    echo "Probando conexión a PostgreSQL:"
    docker compose -f docker-compose.prod.yml exec db pg_isready -U certificados_user -d certificados_prod 2>/dev/null || echo "PostgreSQL no responde"
else
    echo "Servicio PostgreSQL no está ejecutándose"
fi
echo ""

echo -e "${BLUE}=== PASO 11: ANÁLISIS DE PROBLEMAS ===${NC}"
echo "Buscando errores comunes en logs:"

if [ -f "docker-compose.prod.yml" ]; then
    echo "Errores de autenticación Redis:"
    docker compose -f docker-compose.prod.yml logs web 2>/dev/null | grep -i "authentication" | tail -3 || echo "No se encontraron errores de autenticación"
    
    echo ""
    echo "Errores de conexión:"
    docker compose -f docker-compose.prod.yml logs web 2>/dev/null | grep -i "connection" | tail -3 || echo "No se encontraron errores de conexión"
    
    echo ""
    echo "Errores 500:"
    docker compose -f docker-compose.prod.yml logs web 2>/dev/null | grep -i "500" | tail -3 || echo "No se encontraron errores 500"
fi

echo ""
echo -e "${BLUE}=== PASO 12: RECOMENDACIONES ===${NC}"

# Verificar configuración Redis
if [ -f ".env.production" ] && [ -f "docker-compose.prod.yml" ]; then
    REDIS_URL=$(grep "REDIS_URL" .env.production | cut -d'=' -f2)
    REDIS_COMMAND=$(grep -A 5 "redis:" docker-compose.prod.yml | grep "command:" || echo "")
    
    echo "Análisis de configuración Redis:"
    echo "REDIS_URL: $REDIS_URL"
    
    if [[ "$REDIS_URL" == *"redis_password"* ]]; then
        echo -e "${GREEN}✓ REDIS_URL incluye contraseña${NC}"
    else
        echo -e "${RED}✗ REDIS_URL NO incluye contraseña${NC}"
        echo -e "${YELLOW}RECOMENDACIÓN: Actualizar REDIS_URL a redis://:redis_password@redis:6379/0${NC}"
    fi
    
    if [[ "$REDIS_COMMAND" == *"requirepass"* ]]; then
        echo -e "${GREEN}✓ Redis configurado con contraseña en docker-compose${NC}"
    else
        echo -e "${RED}✗ Redis NO configurado con contraseña en docker-compose${NC}"
        echo -e "${YELLOW}RECOMENDACIÓN: Agregar --requirepass a la configuración de Redis${NC}"
    fi
fi

echo ""
echo -e "${BLUE}=== DIAGNÓSTICO COMPLETADO ===${NC}"
echo "Revisa los resultados anteriores para identificar el problema."
echo ""
echo "Comandos útiles para continuar:"
echo "- Ver logs en tiempo real: docker compose -f docker-compose.prod.yml logs web -f"
echo "- Reiniciar servicios: docker compose -f docker-compose.prod.yml restart"
echo "- Detener todo: docker compose -f docker-compose.prod.yml down"
echo "- Iniciar todo: docker compose -f docker-compose.prod.yml up -d"