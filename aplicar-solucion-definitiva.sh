#!/bin/bash

echo "🎯 APLICANDO SOLUCIÓN DEFINITIVA - REDIS"
echo "======================================="
echo ""

# Crear backup del archivo actual
cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backup creado: .env.production.backup.$(date +%Y%m%d_%H%M%S)"

# Verificar qué archivo tiene configuración Redis
echo "🔍 Verificando configuración Redis en archivos..."

REDIS_IN_CORREGIDO=$(grep -c "REDIS_URL" .env.production.CORREGIDO 2>/dev/null || echo "0")
REDIS_IN_LISTO=$(grep -c "REDIS_URL" .env.production.LISTO 2>/dev/null || echo "0")

echo "   Redis en CORREGIDO: $REDIS_IN_CORREGIDO líneas"
echo "   Redis en LISTO: $REDIS_IN_LISTO líneas"

# Usar el archivo que tenga configuración Redis, o CORREGIDO por defecto
if [ "$REDIS_IN_CORREGIDO" -gt "0" ]; then
    echo "📁 Usando .env.production.CORREGIDO (tiene configuración Redis)"
    cp .env.production.CORREGIDO .env.production
elif [ "$REDIS_IN_LISTO" -gt "0" ]; then
    echo "📁 Usando .env.production.LISTO (tiene configuración Redis)"
    cp .env.production.LISTO .env.production
else
    echo "📁 Usando .env.production.CORREGIDO y agregando configuración Redis"
    cp .env.production.CORREGIDO .env.production
    
    # Agregar configuración Redis
    cat >> .env.production << 'EOF'

# ============================================
# REDIS (CACHE Y SESIONES)
# ============================================
REDIS_URL=redis://:3FvkPhxH2zE1mqf5twjTiLra80COcpDn@redis:6379/0
REDIS_PASSWORD=3FvkPhxH2zE1mqf5twjTiLra80COcpDn
CACHE_KEY_PREFIX=certificados_prod
CACHE_TIMEOUT=3600
EOF
fi

# Actualizar IP del servidor (de .99 a .92 si es necesario)
echo "🔧 Actualizando IP del servidor..."
sed -i 's/161.132.47.99/161.132.47.92/g' .env.production

# Mostrar configuración actual
echo ""
echo "📋 CONFIGURACIÓN FINAL:"
echo "   SECRET_KEY: $(grep SECRET_KEY .env.production | cut -d'=' -f2 | cut -c1-20)..."
echo "   ALLOWED_HOSTS: $(grep ALLOWED_HOSTS .env.production | cut -d'=' -f2)"
echo "   DB_PASSWORD: $(grep DB_PASSWORD .env.production | cut -d'=' -f2 | cut -c1-10)..."
echo "   REDIS_URL: $(grep REDIS_URL .env.production | cut -d'=' -f2)"
echo "   REDIS_PASSWORD: $(grep REDIS_PASSWORD .env.production | cut -d'=' -f2 | cut -c1-10)..."

echo ""
echo "🔄 Reiniciando servicios..."

# Reiniciar solo el servicio web primero
docker compose -f docker-compose.prod.yml restart web

echo "⏳ Esperando 30 segundos para que el servicio se estabilice..."
sleep 30

echo ""
echo "🧪 VERIFICACIONES:"

echo "1. Estado de servicios:"
docker compose -f docker-compose.prod.yml ps

echo ""
echo "2. Prueba Redis:"
REDIS_RESULT=$(docker compose -f docker-compose.prod.yml exec redis redis-cli -a 3FvkPhxH2zE1mqf5twjTiLra80COcpDn ping 2>/dev/null)
echo "   Resultado: $REDIS_RESULT"

echo ""
echo "3. Logs recientes del web (últimas 3 líneas):"
docker compose -f docker-compose.prod.yml logs web --tail=3

echo ""
echo "4. Verificar errores de autenticación:"
AUTH_ERRORS=$(docker compose -f docker-compose.prod.yml logs web --tail=20 | grep -c "Authentication required" || echo "0")
echo "   Errores de autenticación en últimos 20 logs: $AUTH_ERRORS"

echo ""
echo "5. Prueba HTTP:"
HTTP_RESULT=$(curl -I http://localhost:7070/admin/ 2>/dev/null | head -1 || echo "No responde")
echo "   Respuesta HTTP: $HTTP_RESULT"

echo ""
echo "🎯 RESULTADO FINAL:"

if [[ "$REDIS_RESULT" == "PONG" ]]; then
    echo "✅ Redis funciona correctamente"
    
    if [ "$AUTH_ERRORS" -eq "0" ]; then
        echo "✅ Sin errores de autenticación"
        echo "🌐 Aplicación disponible en: http://161.132.47.92:7070"
        echo "🔑 Admin: http://161.132.47.92:7070/admin/"
    else
        echo "⚠️  Aún hay algunos errores de autenticación ($AUTH_ERRORS)"
        echo "💡 Espera 2-3 minutos más para que se estabilice completamente"
    fi
else
    echo "❌ Redis aún tiene problemas"
    echo "🔧 Puede necesitar reiniciar todos los servicios:"
    echo "   docker compose -f docker-compose.prod.yml down"
    echo "   docker compose -f docker-compose.prod.yml up -d"
fi

echo ""
echo "📊 Para monitorear:"
echo "   docker compose -f docker-compose.prod.yml logs web -f"
echo ""
echo "🔧 Si persisten problemas:"
echo "   docker compose -f docker-compose.prod.yml restart"