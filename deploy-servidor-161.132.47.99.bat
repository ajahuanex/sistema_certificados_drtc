@echo off
REM Script de despliegue para servidor 161.132.47.99 desde Windows
REM Sistema de Certificados DRTC - Producción
REM Usuario: administrador (Docker ya instalado)

set SERVER_IP=161.132.47.99
set SERVER_USER=administrador
set PROJECT_DIR=/home/administrador/sistema_certificados_drtc
set REPO_URL=https://github.com/ajahuanex/sistema_certificados_drtc.git

echo 🚀 INICIANDO DESPLIEGUE EN SERVIDOR %SERVER_IP%
echo Usuario: %SERVER_USER%
echo Directorio: %PROJECT_DIR%
echo ================================================

echo 1️⃣ Verificando conexión al servidor...
ping -n 1 %SERVER_IP% >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: No se puede conectar al servidor %SERVER_IP%
    pause
    exit /b 1
)
echo ✅ Conexión al servidor OK

echo.
echo 2️⃣ Verificando Docker (ya instalado)...
ssh %SERVER_USER%@%SERVER_IP% "docker --version && docker-compose --version"

echo.
echo 3️⃣ Creando directorio del proyecto...
ssh %SERVER_USER%@%SERVER_IP% "mkdir -p %PROJECT_DIR%"

echo.
echo 4️⃣ Clonando/actualizando repositorio...
ssh %SERVER_USER%@%SERVER_IP% "cd %PROJECT_DIR% && git clone %REPO_URL% . 2>/dev/null || git pull origin main"

echo.
echo 5️⃣ Copiando archivos de configuración...
scp .env.production %SERVER_USER%@%SERVER_IP%:%PROJECT_DIR%/.env.production
scp docker-compose.prod.yml %SERVER_USER%@%SERVER_IP%:%PROJECT_DIR%/docker-compose.prod.yml

echo.
echo 6️⃣ Configurando permisos...
ssh %SERVER_USER%@%SERVER_IP% "cd %PROJECT_DIR% && chmod +x entrypoint.sh"

echo.
echo 7️⃣ Deteniendo servicios anteriores (si existen)...
ssh %SERVER_USER%@%SERVER_IP% "cd %PROJECT_DIR% && docker-compose -f docker-compose.prod.yml down 2>/dev/null || true"

echo.
echo 8️⃣ Construyendo contenedores...
ssh %SERVER_USER%@%SERVER_IP% "cd %PROJECT_DIR% && docker-compose -f docker-compose.prod.yml build"

echo.
echo 9️⃣ Iniciando servicios...
ssh %SERVER_USER%@%SERVER_IP% "cd %PROJECT_DIR% && docker-compose -f docker-compose.prod.yml up -d"

echo.
echo 🔟 Esperando que los servicios se inicien...
timeout /t 30 /nobreak

echo.
echo 1️⃣1️⃣ Ejecutando migraciones...
ssh %SERVER_USER%@%SERVER_IP% "cd %PROJECT_DIR% && docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate"

echo.
echo 1️⃣2️⃣ Creando superusuario...
ssh %SERVER_USER%@%SERVER_IP% "cd %PROJECT_DIR% && docker-compose -f docker-compose.prod.yml exec -T web python manage.py create_superuser_if_not_exists"

echo.
echo 1️⃣3️⃣ Cargando plantilla por defecto...
ssh %SERVER_USER%@%SERVER_IP% "cd %PROJECT_DIR% && docker-compose -f docker-compose.prod.yml exec -T web python manage.py load_default_template"

echo.
echo 1️⃣4️⃣ Verificando estado de servicios...
ssh %SERVER_USER%@%SERVER_IP% "cd %PROJECT_DIR% && docker-compose -f docker-compose.prod.yml ps"

echo.
echo ✅ DESPLIEGUE COMPLETADO
echo ========================
echo 🌐 Aplicación disponible en: http://%SERVER_IP%:7070
echo 🔧 Admin disponible en: http://%SERVER_IP%:7070/admin
echo 📊 Dashboard disponible en: http://%SERVER_IP%:7070/admin/dashboard
echo.
echo Credenciales por defecto:
echo Usuario: admin
echo Contraseña: admin123
echo.
pause