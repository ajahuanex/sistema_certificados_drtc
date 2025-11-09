# 🔑 Solución: Credenciales de Admin

## Problema

Las credenciales `admin/admin123` no funcionan para acceder al panel de administración.

## Solución Rápida

### Opción 1: Usar el comando actualizado (Recomendado)

```bash
# Linux/Mac
python manage.py create_superuser_if_not_exists --update --noinput

# Windows
python manage.py create_superuser_if_not_exists --update --noinput
```

Este comando:
- Actualiza la contraseña del usuario `admin` a `admin123`
- Asegura que el usuario tenga permisos de superusuario
- Actualiza el email a `admin@drtc.gob.pe`

### Opción 2: Usar el script de shell de Django

```bash
python manage.py shell
```

Luego ejecuta:

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Actualizar admin
admin = User.objects.get(username='admin')
admin.set_password('admin123')
admin.email = 'admin@drtc.gob.pe'
admin.is_superuser = True
admin.is_staff = True
admin.is_active = True
admin.save()

print('✓ Contraseña actualizada')
exit()
```

### Opción 3: Crear un nuevo superusuario

```bash
python manage.py createsuperuser
```

Sigue las instrucciones en pantalla para crear un nuevo usuario.

## Credenciales Actualizadas

Después de ejecutar cualquiera de las opciones anteriores:

**Usuario**: `admin`  
**Contraseña**: `admin123`  
**Email**: admin@drtc.gob.pe

**URLs de acceso**:
- Puerto 8000: http://127.0.0.1:8000/admin/
- Puerto 8001: http://127.0.0.1:8001/admin/

## Para Docker/Producción

Si estás usando Docker, las credenciales se configuran automáticamente al iniciar el contenedor.

### Variables de Entorno

Agrega estas variables a tu archivo `.env.production`:

```bash
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@drtc.gob.pe
DJANGO_SUPERUSER_PASSWORD=admin123
```

### Reiniciar Contenedores

```bash
# Detener contenedores
docker-compose -f docker-compose.prod.yml down

# Reconstruir e iniciar
docker-compose -f docker-compose.prod.yml up -d --build

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f web
```

El entrypoint.sh ejecutará automáticamente:
```bash
python manage.py create_superuser_if_not_exists --update --noinput
```

Esto asegura que el usuario admin siempre tenga la contraseña correcta.

## Verificar que Funciona

1. Abre tu navegador
2. Ve a: http://127.0.0.1:8001/admin/
3. Ingresa:
   - Usuario: `admin`
   - Contraseña: `admin123`
4. Deberías ver el panel de administración de Django

## Cambios Realizados

### 1. Comando Mejorado

El comando `create_superuser_if_not_exists` ahora tiene la opción `--update` que:
- Actualiza la contraseña si el usuario ya existe
- No requiere confirmación con `--noinput`
- Usa valores por defecto de variables de entorno

### 2. Entrypoint Actualizado

El archivo `entrypoint.sh` ahora ejecuta:
```bash
python manage.py create_superuser_if_not_exists --update --noinput
```

Esto asegura que cada vez que se inicia el contenedor, las credenciales sean correctas.

### 3. Variables de Entorno

Se agregaron variables de entorno por defecto:
- `DJANGO_SUPERUSER_USERNAME=admin`
- `DJANGO_SUPERUSER_EMAIL=admin@drtc.gob.pe`
- `DJANGO_SUPERUSER_PASSWORD=admin123`

## Seguridad en Producción

⚠️ **IMPORTANTE**: En producción, debes cambiar estas credenciales:

1. Accede al admin con `admin/admin123`
2. Ve a "Usuarios" en el panel de administración
3. Haz clic en el usuario "admin"
4. Cambia la contraseña a una segura
5. Actualiza el email si es necesario

O usa el comando:

```bash
python manage.py changepassword admin
```

## Troubleshooting

### Error: "Usuario no encontrado"

Si el usuario admin no existe, créalo:

```bash
python manage.py create_superuser_if_not_exists --noinput
```

### Error: "Base de datos no disponible"

Asegúrate de que la base de datos esté corriendo:

```bash
# Para PostgreSQL
docker-compose -f docker-compose.prod.yml ps db

# Para desarrollo con SQLite
# No requiere servicio adicional
```

### Error: "Contraseña incorrecta" después de actualizar

1. Limpia la caché del navegador
2. Intenta en modo incógnito
3. Verifica que no haya espacios en la contraseña
4. Ejecuta el comando de actualización nuevamente

## Comandos Útiles

```bash
# Listar todos los superusuarios
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); [print(f'{u.username} - {u.email}') for u in User.objects.filter(is_superuser=True)]"

# Verificar si admin existe
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Existe' if User.objects.filter(username='admin').exists() else 'No existe')"

# Activar usuario admin si está desactivado
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); admin = User.objects.get(username='admin'); admin.is_active = True; admin.save(); print('Usuario activado')"
```

## Resumen

El problema de las credenciales se ha solucionado mediante:

1. ✅ Comando mejorado con opción `--update`
2. ✅ Entrypoint que actualiza credenciales automáticamente
3. ✅ Variables de entorno con valores por defecto
4. ✅ Documentación clara de cómo resetear credenciales

Ahora las credenciales `admin/admin123` funcionarán correctamente tanto en desarrollo como en producción (Docker).
