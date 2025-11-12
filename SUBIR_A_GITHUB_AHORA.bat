@echo off
echo ============================================
echo SUBIENDO CAMBIOS A GITHUB
echo ============================================
echo.

REM Dar permisos de ejecución al entrypoint.sh (Git guardará esto)
git update-index --chmod=+x entrypoint.sh

REM Agregar todos los cambios
git add .

REM Hacer commit
git commit -m "Fix: Configuracion nginx HTTP y permisos entrypoint - Archivos estaticos corregidos"

REM Subir a GitHub
git push origin main

echo.
echo ============================================
echo CAMBIOS SUBIDOS A GITHUB
echo ============================================
echo.
echo Archivos principales actualizados:
echo - entrypoint.sh (con permisos +x)
echo - nginx.prod.http-only.conf (configuracion HTTP)
echo - DESPLIEGUE_HTTP_FINAL.txt (comandos para Ubuntu)
echo - AGREGAR_REVERSE_PROXY_DESPUES.md (guia HTTPS futura)
echo.
echo SIGUIENTE PASO: Ejecutar en Ubuntu
echo.
pause
