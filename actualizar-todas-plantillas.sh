#!/bin/bash
# Script para actualizar TODAS las plantillas de importación

echo "========================================="
echo "ACTUALIZANDO TODAS LAS PLANTILLAS"
echo "========================================="
echo ""

# Copiar todas las plantillas al servidor
echo "1. Copiando plantillas al servidor..."
scp templates/admin/certificates/excel_import.html administrador@161.132.47.92:~/dockers/sistema_certificados_drtc/templates/admin/certificates/
scp templates/admin/certificates/csv_import.html administrador@161.132.47.92:~/dockers/sistema_certificados_drtc/templates/admin/certificates/
scp templates/admin/certificates/csv_validation_result.html administrador@161.132.47.92:~/dockers/sistema_certificados_drtc/templates/admin/certificates/
scp templates/admin/certificates/external_import.html administrador@161.132.47.92:~/dockers/sistema_certificados_drtc/templates/admin/certificates/
scp templates/admin/certificates/pdf_import.html administrador@161.132.47.92:~/dockers/sistema_certificados_drtc/templates/admin/certificates/
scp templates/admin/certificates/final_import.html administrador@161.132.47.92:~/dockers/sistema_certificados_drtc/templates/admin/certificates/
scp templates/admin/dashboard.html administrador@161.132.47.92:~/dockers/sistema_certificados_drtc/templates/admin/

# Conectar y actualizar en el contenedor
ssh administrador@161.132.47.92 << 'EOF'
cd dockers/sistema_certificados_drtc

echo ""
echo "2. Copiando plantillas al contenedor..."
docker cp templates/admin/certificates/excel_import.html certificados_web:/app/templates/admin/certificates/
docker cp templates/admin/certificates/csv_import.html certificados_web:/app/templates/admin/certificates/
docker cp templates/admin/certificates/csv_validation_result.html certificados_web:/app/templates/admin/certificates/
docker cp templates/admin/certificates/external_import.html certificados_web:/app/templates/admin/certificates/
docker cp templates/admin/certificates/pdf_import.html certificados_web:/app/templates/admin/certificates/
docker cp templates/admin/certificates/final_import.html certificados_web:/app/templates/admin/certificates/
docker cp templates/admin/dashboard.html certificados_web:/app/templates/admin/

echo ""
echo "3. Verificando plantillas..."
docker compose -f docker-compose.prod.7070.yml exec -T web ls -lh /app/templates/admin/certificates/ | grep -E 'import|csv'

echo ""
echo "4. Reiniciando contenedor..."
docker compose -f docker-compose.prod.7070.yml restart web

echo ""
echo "5. Esperando 10 segundos..."
sleep 10

echo ""
echo "6. Estado final..."
docker compose -f docker-compose.prod.7070.yml ps

EOF

echo ""
echo "========================================="
echo "ACTUALIZACIÓN COMPLETADA"
echo "========================================="
echo ""
echo "Ahora limpia el cache del navegador con Ctrl+Shift+R"
