@echo off
echo =========================================
echo DIAGNOSTICO DE CONSULTAS POR DNI
echo =========================================
echo.

echo Conectando al servidor de produccion...
ssh administrador@161.132.47.92 "cd dockers/sistema_certificados_drtc && echo '=== 1. Estado de contenedores ===' && docker compose ps && echo '' && echo '=== 2. Logs recientes del web ===' && docker compose logs --tail=30 web && echo '' && echo '=== 3. Verificando base de datos ===' && docker compose exec -T web python manage.py shell -c \"from certificates.models import Participant, Certificate; print('Total participantes:', Participant.objects.count()); print('Total certificados:', Certificate.objects.count()); print('Primeros 5 participantes:'); [print(f'  - DNI: {p.dni} - {p.full_name}') for p in Participant.objects.all()[:5]]\" && echo '' && echo '=== 4. Probando URL de consulta ===' && curl -s -I http://localhost:7070/consulta/"

echo.
echo =========================================
echo DIAGNOSTICO COMPLETADO
echo =========================================
pause
