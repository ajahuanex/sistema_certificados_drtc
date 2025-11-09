@echo off
REM Script para verificar configuración SSL/HTTPS

echo ==========================================
echo Verificacion de Configuracion SSL/HTTPS
echo ==========================================
echo.

REM Configuración
set SSL_DIR=ssl
set CERT_FILE=%SSL_DIR%\cert.pem
set KEY_FILE=%SSL_DIR%\key.pem
set HTTPS_URL=https://localhost:8443

echo 1. Verificando archivos de certificados...
echo.

REM Verificar que existen los archivos
if exist "%CERT_FILE%" (
    echo [OK] Certificado encontrado: %CERT_FILE%
) else (
    echo [ERROR] Certificado NO encontrado: %CERT_FILE%
    echo.
    echo Generar certificado con:
    echo   scripts\generate-ssl-cert.bat
    pause
    exit /b 1
)

if exist "%KEY_FILE%" (
    echo [OK] Clave privada encontrada: %KEY_FILE%
) else (
    echo [ERROR] Clave privada NO encontrada: %KEY_FILE%
    pause
    exit /b 1
)

echo.
echo 2. Verificando validez del certificado...
echo.

REM Verificar que OpenSSL está disponible
where openssl >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] OpenSSL no esta instalado, omitiendo verificaciones avanzadas
    echo        Instalar desde: https://slproweb.com/products/Win32OpenSSL.html
    goto :skip_openssl
)

REM Verificar que el certificado es válido
openssl x509 -in "%CERT_FILE%" -noout -text >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Certificado valido
    
    REM Mostrar información del certificado
    echo.
    echo Informacion del certificado:
    openssl x509 -in "%CERT_FILE%" -noout -subject
    openssl x509 -in "%CERT_FILE%" -noout -issuer
    openssl x509 -in "%CERT_FILE%" -noout -dates
    echo.
    
    REM Verificar si está expirado
    openssl x509 -in "%CERT_FILE%" -noout -checkend 0 >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Certificado no expirado
    ) else (
        echo [ERROR] Certificado EXPIRADO
        echo         Regenerar con: scripts\generate-ssl-cert.bat
    )
    
    REM Advertir si expira pronto (30 días = 2592000 segundos)
    openssl x509 -in "%CERT_FILE%" -noout -checkend 2592000 >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo [WARN] Certificado expira en menos de 30 dias
    )
) else (
    echo [ERROR] Certificado invalido o corrupto
    pause
    exit /b 1
)

echo.
echo 3. Verificando que clave y certificado coinciden...
echo.

REM Verificar que la clave privada coincide con el certificado
for /f "delims=" %%i in ('openssl x509 -noout -modulus -in "%CERT_FILE%" ^| openssl md5') do set CERT_MODULUS=%%i
for /f "delims=" %%i in ('openssl rsa -noout -modulus -in "%KEY_FILE%" 2^>nul ^| openssl md5') do set KEY_MODULUS=%%i

if "%CERT_MODULUS%"=="%KEY_MODULUS%" (
    echo [OK] Clave privada coincide con certificado
) else (
    echo [ERROR] Clave privada NO coincide con certificado
    echo         Regenerar ambos con: scripts\generate-ssl-cert.bat
    pause
    exit /b 1
)

:skip_openssl

echo.
echo 4. Verificando configuración de nginx...
echo.

REM Verificar que nginx está corriendo
docker-compose ps | findstr /C:"nginx" | findstr /C:"Up" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Nginx esta ejecutandose
    
    REM Verificar configuración de nginx
    docker-compose exec -T nginx nginx -t >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Configuracion de nginx valida
    ) else (
        echo [ERROR] Configuracion de nginx invalida
        docker-compose exec nginx nginx -t
        pause
        exit /b 1
    )
) else (
    echo [WARN] Nginx no esta ejecutandose
    echo        Iniciar con: docker-compose up -d nginx
)

echo.
echo 5. Verificando conectividad HTTPS...
echo.

REM Verificar que curl está disponible
where curl >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    REM Intentar conexión HTTPS (ignorando verificación de certificado auto-firmado)
    for /f %%i in ('curl -k -s -o nul -w "%%{http_code}" "%HTTPS_URL%/health/" 2^>nul') do set HTTP_CODE=%%i
    
    if "%HTTP_CODE%"=="200" (
        echo [OK] Servidor HTTPS responde correctamente
        
        REM Verificar redirección HTTP -> HTTPS
        for /f %%i in ('curl -s -o nul -w "%%{http_code}" "http://localhost:8181/" 2^>nul') do set HTTP_REDIRECT=%%i
        if "%HTTP_REDIRECT%"=="301" (
            echo [OK] Redireccion HTTP -^> HTTPS configurada
        ) else if "%HTTP_REDIRECT%"=="302" (
            echo [OK] Redireccion HTTP -^> HTTPS configurada
        ) else (
            echo [WARN] Redireccion HTTP -^> HTTPS no detectada (codigo: %HTTP_REDIRECT%)
        )
        
        REM Verificar headers de seguridad
        echo.
        echo   Verificando headers de seguridad...
        
        curl -k -s -I "%HTTPS_URL%/" 2>nul | findstr /I "strict-transport-security" >nul
        if %ERRORLEVEL% EQU 0 (
            echo   [OK] HSTS habilitado
        ) else (
            echo   [WARN] HSTS no detectado
        )
        
        curl -k -s -I "%HTTPS_URL%/" 2>nul | findstr /I "x-frame-options" >nul
        if %ERRORLEVEL% EQU 0 (
            echo   [OK] X-Frame-Options configurado
        ) else (
            echo   [WARN] X-Frame-Options no detectado
        )
        
        curl -k -s -I "%HTTPS_URL%/" 2>nul | findstr /I "x-content-type-options" >nul
        if %ERRORLEVEL% EQU 0 (
            echo   [OK] X-Content-Type-Options configurado
        ) else (
            echo   [WARN] X-Content-Type-Options no detectado
        )
    ) else (
        echo [ERROR] Servidor HTTPS no responde (codigo: %HTTP_CODE%)
        echo         Verificar logs: docker-compose logs nginx
    )
) else (
    echo [WARN] curl no esta instalado, omitiendo pruebas de conectividad
)

echo.
echo ==========================================
echo Resumen de Verificacion
echo ==========================================
echo.
echo Certificados SSL configurados
echo.
echo Proximos pasos:
echo   * Acceder a: %HTTPS_URL%
echo   * Para produccion, usar Let's Encrypt
echo   * Configurar renovacion automatica
echo.
echo Documentacion completa: docs\SSL_CONFIGURATION.md
echo.
pause
