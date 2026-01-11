#!/bin/bash

# Diagnóstico rápido para identificar el problema Redis

echo "🔍 DIAGNÓSTICO RÁPIDO - PROBLEMA REDIS"
echo "======================================"
echo ""

# Verificar archivos
echo "📁 Archivos del proyecto:"
ls -la | grep -E "(docker-compose.prod.yml|\.env\.production)" | awk '{print "   " $9 " - " $5 " bytes"}'
echo ""

# Configuración Redis actual
echo "⚙️  Configuración Redis actual:"
echo "   REDIS_URL: $(grep REDIS_URL .env.production 2>/dev/null || echo 'NO ENCONTRADO')"
echo "   REDIS_PASSWORD: $(grep REDIS_PASSWORD .env.production 2>/dev/null || echo 'NO ENCONTRADO')"
echo ""

# Estado servicios
echo "🐳 Estado de contenedores:"
docker compose -f docker-compose.prod.yml ps 2>/dev/null || echo "   ❌ No se puede verificar estado"
echo ""

# Prueba Redis
echo "🔴 Prueba Redis:"
echo -n "   Sin contraseña: "
docker compose -f docker-compose.prod.yml exec redis redis-cli ping 2>/dev/null || echo "❌ FALLA"

echo -n "   Con contraseña: "
docker compose -f docker-compose.prod.yml exec redis redis-cli -a redis_password ping 2>/dev/null || echo "❌ FALLA"
echo ""

# Último error
echo "🚨 Último error de autenticación:"
docker compose -f docker-compose.prod.yml logs web --tail=50 2>/dev/null | grep -i "authentication" | tail -1 || echo "   No se encontraron errores recientes"
echo ""

# Diagnóstico
echo "🎯 DIAGNÓSTICO:"
REDIS_URL=$(grep REDIS_URL .env.production 2>/dev/null)
REDIS_CONFIG=$(grep -A 5 "redis:" docker-compose.prod.yml 2>/dev/null | grep "command:")

if [[ "$REDIS_URL" == *"redis_password"* ]]; then
    echo "   ✅ REDIS_URL tiene contraseña configurada"
else
    echo "   ❌ REDIS_URL NO tiene contraseña configurada"
    echo "      Actual: $REDIS_URL"
    echo "      Debería ser: redis://:redis_password@redis:6379/0"
fi

if [[ "$REDIS_CONFIG" == *"requirepass"* ]]; then
    echo "   ✅ Redis configurado con contraseña en docker-compose"
else
    echo "   ❌ Redis NO configurado con contraseña en docker-compose"
    echo "      Falta: --requirepass \${REDIS_PASSWORD:-redis_password}"
fi

echo ""
echo "🔧 SOLUCIÓN RECOMENDADA:"
if [[ "$REDIS_URL" != *"redis_password"* ]] || [[ "$REDIS_CONFIG" != *"requirepass"* ]]; then
    echo "   Ejecutar: ./fix-redis-remoto.sh"
    echo "   O manualmente:"
    echo "   1. Actualizar REDIS_URL en .env.production"
    echo "   2. Agregar --requirepass en docker-compose.prod.yml"
    echo "   3. Reiniciar servicios"
else
    echo "   ✅ Configuración parece correcta"
    echo "   Probar reiniciar servicios: docker compose -f docker-compose.prod.yml restart"
fi