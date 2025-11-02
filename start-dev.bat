@echo off
REM Script de Inicio Rápido para Desarrollo - Windows
REM Sistema de Certificados DRTC

echo.
echo ==========================================
echo 🚀 Sistema de Certificados DRTC
echo    Modo Desarrollo
echo ==========================================
echo.

REM Verificar Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no esta instalado
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose no esta instalado
    pause
    exit /b 1
)

echo ✅ Docker y Docker Compose disponibles

REM Crear directorios necesarios
echo.
echo 📁 Creando directorios necesarios...
if not exist "media" mkdir media
if not exist "staticfiles" mkdir staticfiles
if not exist "logs" mkdir logs
if not exist "backups" mkdir backups

REM Construir y levantar servicios
echo.
echo 🔨 Construyendo imagenes...
docker-compose build

echo.
echo 🚀 Levantando servicios...
docker-compose up -d

REM Esperar a que los servicios estén listos
echo.
echo ⏳ Esperando a que los servicios esten listos...
timeout /t 10 /nobreak >nul

REM Ejecutar migraciones
echo.
echo 🗄️  Ejecutando migraciones...
docker-compose exec web python manage.py migrate

REM Recopilar archivos estáticos
echo.
echo 📦 Recopilando archivos estaticos...
docker-compose exec web python manage.py collectstatic --noinput

REM Crear superusuario si no existe
echo.
echo 👤 Configurando superusuario...
docker-compose exec web python manage.py create_superuser_if_not_exists

REM Cargar plantilla por defecto
echo.
echo 📄 Cargando plantilla por defecto...
docker-compose exec web python manage.py load_default_template

echo.
echo ✅ ¡Sistema iniciado correctamente!
echo.
echo 🌐 Aplicacion disponible en: http://localhost:8000
echo 🔧 Panel de administracion: http://localhost:8000/admin/
echo 🗄️  Adminer (BD): http://localhost:8080
echo.
echo 📊 Para ver logs en tiempo real:
echo    docker-compose logs -f web
echo.
echo 🛑 Para detener el sistema:
echo    docker-compose down
echo.
echo 🔄 Para reiniciar un servicio:
echo    docker-compose restart web
echo.

REM Mostrar estado de los servicios
echo 📋 Estado de los servicios:
docker-compose ps

echo.
echo Presione cualquier tecla para continuar...
pause >nul