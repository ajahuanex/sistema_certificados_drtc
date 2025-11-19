#!/bin/bash
# Script para actualizar archivos estáticos del dashboard en producción

echo "========================================="
echo "ACTUALIZANDO ARCHIVOS ESTÁTICOS"
echo "========================================="
echo ""

# Copiar archivos al servidor
echo "1. Copiando archivos CSS y JS al servidor..."
scp static/admin/css/dashboard.css administrador@161.132.47.92:~/dockers/sistema_certificados_drtc/static/admin/css/
scp static/admin/js/dashboard.js administrador@161.132.47.92:~/dockers/sistema_certificados_drtc/static/admin/js/

# Conectar y actualizar
ssh administrador@161.132.47.92 << 'EOF'
cd dockers/sistema_certificados_drtc

echo ""
echo "2. Verificando archivos copiados..."
ls -lh static/admin/css/dashboard.css
ls -lh static/admin/js/dashboard.js

echo ""
echo "3. Copiando archivos al contenedor..."
docker cp static/admin/css/dashboard.css certificados_web:/app/static/admin/css/
docker cp static/admin/js/dashboard.js certificados_web:/app/static/admin/js/

echo ""
echo "4. Recolectando archivos estáticos..."
docker compose -f docker-compose.prod.7070.yml exec -T web python manage.py collectstatic --noinput

echo ""
echo "5. Verificando archivos en staticfiles..."
docker compose -f docker-compose.prod.7070.yml exec -T web ls -lh /app/staticfiles/admin/css/dashboard.css
docker compose -f docker-compose.prod.7070.yml exec -T web ls -lh /app/staticfiles/admin/js/dashboard.js

echo ""
echo "6. Reiniciando web para limpiar cache..."
docker compose -f docker-compose.prod.7070.yml restart web

EOF

echo ""
echo "========================================="
echo "ACTUALIZACIÓN COMPLETADA"
echo "========================================="
echo ""
echo "Ahora recarga el dashboard con Ctrl+Shift+R"
echo "URL: https://certificados.transportespuno.gob.pe/admin/dashboard/"
