#!/bin/bash

echo "🚨 SOLUCIONANDO ERROR CSRF 403..."
echo "=================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: No se encuentra docker-compose.yml"
    echo "   Asegúrate de estar en el directorio del proyecto"
    exit 1
fi

# Verificar que existe .env.production
if [ ! -f ".env.production" ]; then
    echo "❌ Error: No se encuentra .env.production"
    exit 1
fi

echo "✅ Archivos encontrados"

# Verificar si ya existe CSRF_TRUSTED_ORIGINS
if grep -q "CSRF_TRUSTED_ORIGINS" .env.production; then
    echo "⚠️  CSRF_TRUSTED_ORIGINS ya existe en .env.production"
    echo "   Actualizando valor..."
    
    # Crear backup
    cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S)
    
    # Remover línea existente y agregar nueva
    grep -v "CSRF_TRUSTED_ORIGINS" .env.production > .env.production.tmp
    echo "CSRF_TRUSTED_ORIGINS=https://certificados.transportespuno.gob.pe,http://certificados.transportespuno.gob.pe,http://161.132.47.92,https://161.132.47.92" >> .env.production.tmp
    mv .env.production.tmp .env.production
else
    echo "➕ Agregando CSRF_TRUSTED_ORIGINS a .env.production"
    echo "CSRF_TRUSTED_ORIGINS=https://certificados.transportespuno.gob.pe,http://certificados.transportespuno.gob.pe,http://161.132.47.92,https://161.132.47.92" >> .env.production
fi

echo "✅ CSRF_TRUSTED_ORIGINS configurado"

# Mostrar la configuración
echo ""
echo "📋 Configuración CSRF actual:"
echo "=============================="
grep "CSRF_TRUSTED_ORIGINS" .env.production

echo ""
echo "🔄 Reiniciando aplicación..."
docker compose restart web

echo ""
echo "⏳ Esperando que la aplicación se reinicie..."
sleep 15

echo ""
echo "🧪 Probando la aplicación..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:7070/admin/)

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ ¡ÉXITO! La aplicación responde correctamente"
    echo "   Status: $HTTP_STATUS"
    echo ""
    echo "🌐 Acceso:"
    echo "   Directo: http://161.132.47.92:7070/admin/"
    echo "   Con proxy: http://certificados.transportespuno.gob.pe/admin/"
    echo ""
    echo "👤 Credenciales:"
    echo "   Usuario: admin"
    echo "   Contraseña: admin123"
else
    echo "⚠️  La aplicación responde con status: $HTTP_STATUS"
    echo "   Revisando logs..."
    echo ""
    docker compose logs web --tail=20
fi

echo ""
echo "🔧 Comandos útiles:"
echo "   Ver logs: docker compose logs web -f"
echo "   Estado: docker compose ps"
echo "   Reiniciar: docker compose restart web"

echo ""
echo "✅ Script completado"