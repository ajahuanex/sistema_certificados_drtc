@echo off
echo Reseteando contraseña del admin...
echo.

python -c "import os; os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.base'; import django; django.setup(); from django.contrib.auth import get_user_model; User = get_user_model(); admin = User.objects.get(username='admin'); admin.set_password('admin123'); admin.save(); print('Contraseña actualizada para admin')"

if errorlevel 1 (
    echo Error al actualizar contraseña
    pause
    exit /b 1
)

echo.
echo ========================================
echo Credenciales actualizadas:
echo Usuario: admin
echo Contraseña: admin123
echo URL: http://127.0.0.1:8001/admin/
echo ========================================
echo.
pause
