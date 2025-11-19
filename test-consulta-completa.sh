#!/bin/bash
# Script para probar consulta completa con CSRF

echo "========================================="
echo "PRUEBA COMPLETA DE CONSULTA"
echo "========================================="
echo ""

# Conectar al servidor y hacer prueba completa
ssh administrador@161.132.47.92 << 'EOF'
cd dockers/sistema_certificados_drtc

echo "1. Obteniendo página de consulta y CSRF token..."
RESPONSE=$(curl -s -c cookies.txt https://certificados.transportespuno.gob.pe/consulta/)
CSRF_TOKEN=$(echo "$RESPONSE" | grep -oP 'csrfmiddlewaretoken.*?value="\K[^"]+' | head -1)

if [ -z "$CSRF_TOKEN" ]; then
    echo "❌ No se pudo obtener CSRF token"
    echo "Intentando extraer de cookie..."
    CSRF_TOKEN=$(grep csrftoken cookies.txt | awk '{print $7}')
fi

echo "CSRF Token: $CSRF_TOKEN"
echo ""

echo "2. Haciendo POST con DNI de prueba..."
curl -s -b cookies.txt -c cookies.txt \
  -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Referer: https://certificados.transportespuno.gob.pe/consulta/" \
  -d "csrfmiddlewaretoken=$CSRF_TOKEN&dni=12345678" \
  https://certificados.transportespuno.gob.pe/consulta/ \
  -w "\nHTTP Status: %{http_code}\n" \
  -o response.html

echo ""
echo "3. Verificando respuesta..."
if grep -q "Server Error (500)" response.html; then
    echo "❌ ERROR 500 detectado"
    echo "Mostrando logs recientes:"
    docker compose -f docker-compose.prod.7070.yml logs --tail=20 web | grep -A 10 "Error\|Exception"
elif grep -q "Forbidden (403)" response.html; then
    echo "⚠️  Error 403 CSRF"
    echo "Verificando configuración CSRF..."
    grep CSRF_TRUSTED .env.production
elif grep -q "No se encontraron certificados" response.html || grep -q "certificados" response.html; then
    echo "✅ Consulta funcionando correctamente"
    echo "Respuesta: No hay certificados para ese DNI (esperado)"
else
    echo "📄 Respuesta recibida:"
    head -50 response.html
fi

echo ""
echo "4. Limpiando archivos temporales..."
rm -f cookies.txt response.html

echo ""
echo "5. Estado actual de contenedores:"
docker compose -f docker-compose.prod.7070.yml ps

EOF

echo ""
echo "========================================="
echo "PRUEBA COMPLETADA"
echo "========================================="
