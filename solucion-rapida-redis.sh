#!/bin/bash

echo "🚀 SOLUCIÓN RÁPIDA - PROBLEMA REDIS"
echo "=================================="
echo ""

# Crear backup del archivo actual
cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backup creado del archivo actual"

# Verificar qué archivo de respaldo usar
if [ -f ".env.production.LISTO" ]; then
    echo "📁 Usando .env.production.LISTO como base"
    cp .env.production.LISTO .env.production
elif [ -f ".env.production.CORREGIDO" ]; then
    echo "📁 Usando .env.production.CORREGIDO como base"
    cp .env.production.CORREGIDO .env.production
else
    echo "❌ No se encontraron archivos de respaldo completos"
    exit 1
fi

# Actualizar la IP del servidor (cambiar de 161.132.47.99 a 161.132.47.92)
echo "🔧 Actualizando IP del servidor..."
sed -i 's/161.132.47.99/161.132.47.92/g' .env.production

# Verificar que tenga la configuración Redis correcta
echo "🔍 Verificando configuración Redis..."
if grep -q "REDIS_URL=redis://:.*@redis:6379/0" .env.production; then
    echo "✅ REDIS_URL configurado correctamente"
else
    echo "🔧 Agregando configuración Redis..."
    cat >> .env.production << 'EOF'

# Redis Configuration
REDIS_URL=redis://:redis_password@redis:6379/0
REDIS_PASSWORD=redis_password
CACHE_TIMEOUT=3600
CACHE_KEY_PREFIX=certificados_prod
EOF
fi

echo ""
echo "📋 Configuración Redis actual:"
grep -E "REDIS|CACHE" .env.production

echo ""
echo "🔄 Reiniciando solo el servicio web..."
docker compose -f docker-compose.prod.yml restart web

echo ""
echo "⏳ Esperando 30 segundos..."
sleep 30

echo ""
echo "🧪 VERIFICACIONES:"

echo "1. Estado de servicios:"
docker compose -f docker-compose.prod.yml ps

echo ""
echo "2. Prueba Redis con contraseña:"
docker compose -f docker-compose.prod.yml exec redis redis-cli -a redis_password ping

echo ""
echo "3. Logs recientes del web (últimas 5 líneas):"
docker compose -f docker-compose.prod.yml logs web --tail=5

echo ""
echo "4. Prueba de la aplicación:"
curl -I http://localhost:7070/admin/ 2>/dev/null | head -1 || echo "❌ Aplicación no responde aún"

echo ""
echo "🎯 RESULTADO:"
if docker compose -f docker-compose.prod.yml exec redis redis-cli -a redis_password ping | grep -q "PONG"; then
    echo "✅ Redis funciona correctamente"
    
    # Verificar si el web ya no tiene errores de autenticación
    if ! docker compose -f docker-compose.prod.yml logs web --tail=10 | grep -q "Authentication required"; then
        echo "✅ Aplicación web sin errores de autenticación"
        echo "🌐 Aplicación disponible en: http://161.132.47.92:7070"
    else
        echo "⚠️  Aplicación aún tiene errores de autenticación"
        echo "💡 Puede necesitar unos minutos más para estabilizarse"
    fi
else
    echo "❌ Redis aún tiene problemas"
fi

echo ""
echo "📊 Para monitorear en tiempo real:"
echo "docker compose -f docker-compose.prod.yml logs web -f"