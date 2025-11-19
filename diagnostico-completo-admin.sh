#!/bin/bash
# Diagnóstico completo del admin

echo "========================================="
echo "DIAGNOSTICO COMPLETO - ADMIN"
echo "========================================="
echo ""

ssh administrador@161.132.47.92 << 'EOF'
cd dockers/sistema_certificados_drtc

echo "=== 1. Estado de contenedores ==="
docker compose -f docker-compose.prod.7070.yml ps

echo ""
echo "=== 2. Verificando Redis ==="
docker compose -f docker-compose.prod.7070.yml exec -T redis redis-cli -a redis_password ping

echo ""
echo "=== 3. Verificando PostgreSQL ==="
docker compose -f docker-compose.prod.7070.yml exec -T postgres psql -U certificados_user -d certificados_prod -c "SELECT COUNT(*) as total_eventos FROM certificates_event;"

echo ""
echo "=== 4. Verificando configuración ==="
grep -E "(REDIS_URL|DB_HOST|CSRF_TRUSTED)" .env.production

echo ""
echo "=== 5. Probando dashboard ==="
curl -s -o /dev/null -w "Dashboard: %{http_code}\n" http://localhost:7070/admin/dashboard/

echo ""
echo "=== 6. Probando importación Excel ==="
curl -s -o /dev/null -w "Import Excel: %{http_code}\n" http://localhost:7070/admin/certificates/import-excel/

echo ""
echo "=== 7. Probando importación CSV ==="
curl -s -o /dev/null -w "Import CSV: %{http_code}\n" http://localhost:7070/admin/certificates/import-csv/

echo ""
echo "=== 8. Últimos logs (sin health checks) ==="
docker compose -f docker-compose.prod.7070.yml logs --tail=20 web | grep -v health | tail -15

EOF

echo ""
echo "========================================="
echo "DIAGNOSTICO COMPLETADO"
echo "========================================="
