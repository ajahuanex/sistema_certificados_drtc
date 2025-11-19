@echo off
echo ==========================================
echo 🚀 CONTINUANDO DESPLIEGUE EN PRODUCCIÓN
echo ==========================================
echo.

REM Paso 1: Crear migraciones faltantes
echo 📝 Paso 1: Creando migraciones...
docker compose exec web python manage.py makemigrations
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error al crear migraciones
    exit /b 1
)
echo ✅ Migraciones creadas
echo.

REM Paso 2: Aplicar migraciones
echo 📝 Paso 2: Aplicando migraciones...
docker compose exec web python manage.py migrate
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error al aplicar migraciones
    exit /b 1
)
echo ✅ Migraciones aplicadas
echo.

REM Paso 3: Recolectar archivos estáticos
echo 📝 Paso 3: Recolectando archivos estáticos...
docker compose exec web python manage.py collectstatic --noinput
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error al recolectar archivos estáticos
    exit /b 1
)
echo ✅ Archivos estáticos recolectados
echo.

REM Paso 4: Crear superusuario
echo 📝 Paso 4: Creando superusuario...
docker compose exec web python manage.py create_superuser_if_not_exists --noinput
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error al crear superusuario
    exit /b 1
)
echo ✅ Superusuario creado
echo.

REM Paso 5: Verificar estado de contenedores
echo 📝 Paso 5: Verificando estado de contenedores...
docker compose ps
echo.

REM Paso 6: Probar endpoint de salud
echo 📝 Paso 6: Probando endpoint de salud...
curl -f http://localhost:7070/health/
echo.
echo.

echo ==========================================
echo ✅ DESPLIEGUE COMPLETADO
echo ==========================================
echo.
echo 🌐 Acceso a la aplicación:
echo    URL: http://161.132.47.92:7070/admin/
echo    Usuario: admin
echo    Contraseña: admin123
echo.
echo 📊 Verificar logs:
echo    docker compose logs -f web
echo.
pause
