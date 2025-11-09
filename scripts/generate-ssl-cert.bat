@echo off
REM Script para generar certificados SSL auto-firmados para desarrollo/testing
REM NO usar en producción - usar Let's Encrypt o certificados comerciales

echo ==========================================
echo Generador de Certificados SSL Auto-firmados
echo ==========================================
echo.
echo ADVERTENCIA: Este script genera certificados auto-firmados
echo Solo usar para desarrollo y testing local
echo Para produccion, usar Let's Encrypt o certificados comerciales
echo.

REM Verificar que OpenSSL está instalado
where openssl >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: OpenSSL no esta instalado o no esta en el PATH
    echo.
    echo Opciones de instalacion:
    echo 1. Instalar Git for Windows (incluye OpenSSL)
    echo 2. Descargar desde: https://slproweb.com/products/Win32OpenSSL.html
    echo 3. Usar WSL (Windows Subsystem for Linux)
    pause
    exit /b 1
)

REM Crear directorio SSL si no existe
if not exist "ssl" mkdir ssl

REM Configuración por defecto
set COUNTRY=PE
set STATE=Lima
set CITY=Lima
set ORGANIZATION=DRTC
set COMMON_NAME=localhost
set DAYS=365

REM Solicitar configuración (opcional)
set /p input_cn="Nombre de dominio (default: localhost): "
if not "%input_cn%"=="" set COMMON_NAME=%input_cn%

set /p input_days="Dias de validez (default: 365): "
if not "%input_days%"=="" set DAYS=%input_days%

echo.
echo Generando certificados con la siguiente configuracion:
echo   Pais: %COUNTRY%
echo   Estado: %STATE%
echo   Ciudad: %CITY%
echo   Organizacion: %ORGANIZATION%
echo   Dominio: %COMMON_NAME%
echo   Validez: %DAYS% dias
echo.

REM Generar clave privada y certificado
echo Generando clave privada y certificado...
openssl req -x509 -nodes -days %DAYS% -newkey rsa:2048 ^
  -keyout ssl/key.pem ^
  -out ssl/cert.pem ^
  -subj "/C=%COUNTRY%/ST=%STATE%/L=%CITY%/O=%ORGANIZATION%/CN=%COMMON_NAME%"

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Fallo al generar certificados
    pause
    exit /b 1
)

echo Certificado generado exitosamente
echo.

REM Preguntar por Diffie-Hellman
set /p generate_dh="Generar parametros Diffie-Hellman? (mejora seguridad, toma ~1 minuto) [y/N]: "
if /i "%generate_dh%"=="y" (
    echo Generando parametros Diffie-Hellman (esto puede tardar un momento)...
    openssl dhparam -out ssl/dhparam.pem 2048
    echo Parametros DH generados
    echo.
    echo Para usar DH params, descomenta esta linea en nginx.prod.conf:
    echo   ssl_dhparam /etc/nginx/ssl/dhparam.pem;
    echo.
)

REM Mostrar información del certificado
echo Informacion del certificado:
openssl x509 -in ssl/cert.pem -noout -subject -dates

echo.
echo Certificados SSL generados en el directorio: ssl/
echo.
echo Archivos creados:
echo   - ssl/cert.pem (certificado publico)
echo   - ssl/key.pem (clave privada)
if /i "%generate_dh%"=="y" (
    echo   - ssl/dhparam.pem (parametros DH)
)
echo.
echo Proximos pasos:
echo   1. Reiniciar nginx: docker-compose restart nginx
echo   2. Acceder a: https://%COMMON_NAME%
echo   3. Aceptar la advertencia de seguridad del navegador
echo.
echo RECUERDA: Para produccion, usar Let's Encrypt o certificados comerciales
echo.
pause
