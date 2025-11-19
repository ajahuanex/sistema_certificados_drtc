@echo off
echo =========================================
echo VERIFICACION COMPLETA DE PRODUCCION
echo Servidor: 161.132.47.92:7070
echo =========================================
echo.

echo [1/6] Verificando conectividad al servidor...
ping -n 2 161.132.47.92

echo.
echo [2/6] Verificando estado de contenedores Docker...
ssh administrador@161.132.47.92 "cd dockers/sistema_certificados_drtc && docker compose ps"

echo.
echo [3/6] Verificando logs recientes (ultimas 20 lineas)...
ssh administrador@161.132.47.92 "cd dockers/sistema_certificados_drtc && docker compose logs --tail=20 web"

echo.
echo [4/6] Verificando base de datos...
ssh administrador@161.132.47.92 "cd dockers/sistema_certificados_drtc && docker compose exec -T web python manage.py shell -c \"from certificates.models import Participant, Certificate; print('=== ESTADISTICAS ==='); print(f'Total participantes: {Participant.objects.count()}'); print(f'Total certificados: {Certificate.objects.count()}'); print('\\n=== PRIMEROS 5 PARTICIPANTES ==='); [print(f'{i+1}. DNI: {p.dni} - {p.full_name}') for i, p in enumerate(Participant.objects.all()[:5])]\""

echo.
echo [5/6] Probando acceso HTTP al puerto 7070...
curl -I http://161.132.47.92:7070/

echo.
echo [6/6] Probando URL de consulta...
curl -I http://161.132.47.92:7070/consulta/

echo.
echo =========================================
echo VERIFICACION COMPLETADA
echo =========================================
echo.
echo Presiona cualquier tecla para salir...
pause >nul
