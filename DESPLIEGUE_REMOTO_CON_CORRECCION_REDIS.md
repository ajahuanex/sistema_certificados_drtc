# 🚀 Despliegue Remoto con Corrección Redis - Servidor 161.132.47.92

## 📋 Preparación Local

### 1. Subir cambios a GitHub
```bash
git add .
git commit -m "Fix: Configuración Redis opcional - Cache en memoria como fallback"
git push origin main
```

## 🔐 Conexión al Servidor Remoto

### Conectar por SSH
```bash
ssh root@161.132.47.92
```

## 📥 Actualización del Código en el Servidor

### 1. Navegar al directorio del proyecto
```bash
cd /root/sistema-certificados-drtc
```

### 2. Hacer backup de configuración actual
```bash
cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S)
cp docker-compose.prod.yml docker-compose.prod.yml.backup.$(date +%Y%m%d_%H%M%S)
```

### 3. Actualizar código desde GitHub
```bash
git fetch origin
git reset --hard origin/main
git pull origin main
```

### 4. Verificar archivos actualizados
```bash
echo "=== Verificando archivos clave ==="
echo "1. Configuración Redis en production.py:"
grep -A 10 "USE_REDIS" config/settings/production.py

echo "2. Variable USE_REDIS en .env.production:"
grep "USE_REDIS" .env.production

echo "3. Redis comentado en docker-compose:"
grep -A 5 "redis:" docker-compose.prod.yml
```

## 🛠️ Configuración del Sistema

### 1. Detener servicios actuales
```bash
docker-compose -f docker-compose.prod.yml down
```

### 2. Limpiar contenedores y volúmenes antiguos
```bash
# Limpiar contenedores
docker container prune -f

# Limpiar imágenes no utilizadas
docker image prune -f

# Verificar volúmenes (NO eliminar postgres_data_prod)
docker volume ls
```

### 3. Construir nueva imagen con correcciones
```bash
docker-compose -f docker-compose.prod.yml build --no-cache web
```

### 4. Iniciar servicios (SIN Redis)
```bash
# Iniciar solo los servicios necesarios
docker-compose -f docker-compose.prod.yml up -d db nginx web

# Verificar estado
docker-compose -f docker-compose.prod.yml ps
```

### 5. Esperar que los servicios estén listos
```bash
echo "Esperando que PostgreSQL esté listo..."
sleep 30

# Verificar logs de la base de datos
docker-compose -f docker-compose.prod.yml logs db | tail -10
```

## 🔧 Configuración de Django

### 1. Ejecutar migraciones
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

### 2. Crear superusuario si no existe
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py create_superuser_if_not_exists
```

### 3. Recolectar archivos estáticos
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### 4. Cargar plantilla por defecto
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py load_default_template
```

## ✅ Verificación del Sistema

### 1. Verificar configuración de cache
```bash
docker-compose -f docker-compose.prod.yml exec web python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()
from django.conf import settings
from django.core.cache import cache

print('=== CONFIGURACIÓN DE CACHE ===')
print(f'USE_REDIS: {getattr(settings, \"USE_REDIS\", \"No definido\")}')
print(f'Cache Backend: {settings.CACHES[\"default\"][\"BACKEND\"]}')
print(f'Session Engine: {settings.SESSION_ENGINE}')

print('\n=== PRUEBA DE CACHE ===')
cache.set('test_key', 'test_value', 60)
value = cache.get('test_key')
print(f'Cache test: {\"✓ OK\" if value == \"test_value\" else \"✗ FAIL\"}')
"
```

### 2. Verificar logs de la aplicación
```bash
docker-compose -f docker-compose.prod.yml logs --tail=20 web
```

### 3. Verificar estado de todos los servicios
```bash
docker-compose -f docker-compose.prod.yml ps
```

### 4. Probar conectividad HTTP
```bash
curl -I http://localhost:7070
curl -I http://161.132.47.92:7070
```

## 🌐 Verificación Externa

### Desde tu máquina local, probar:
```bash
# Página principal
curl -I http://161.132.47.92:7070

# Panel de administración
curl -I http://161.132.47.92:7070/admin/

# Health check (si está disponible)
curl http://161.132.47.92:7070/health/
```

## 📊 Monitoreo Continuo

### 1. Monitorear logs en tiempo real
```bash
# En una terminal separada
docker-compose -f docker-compose.prod.yml logs -f web
```

### 2. Verificar uso de recursos
```bash
docker stats
```

### 3. Verificar espacio en disco
```bash
df -h
docker system df
```

## 🔧 Comandos de Troubleshooting

### Si hay problemas con la base de datos:
```bash
# Verificar conexión a PostgreSQL
docker-compose -f docker-compose.prod.yml exec db psql -U certificados_user -d certificados_prod -c "\dt"
```

### Si hay problemas con permisos:
```bash
# Verificar permisos de archivos
ls -la media/ staticfiles/
chown -R 1000:1000 media/ staticfiles/
```

### Si hay problemas con Nginx:
```bash
# Verificar configuración de Nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Recargar configuración
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

## 📝 Verificación Final

### El sistema debería estar disponible en:
- **URL Principal**: http://161.132.47.92:7070
- **Panel Admin**: http://161.132.47.92:7070/admin/
- **Credenciales**: admin / admin123

### Funcionalidades a probar:
1. ✅ Acceso a la página principal
2. ✅ Login en el panel de administración
3. ✅ Importación de participantes (CSV/Excel)
4. ✅ Generación de certificados
5. ✅ Consulta pública de certificados
6. ✅ Dashboard de estadísticas

## 🎯 Estado Esperado

- ✅ Sistema funcionando SIN Redis
- ✅ Cache en memoria local
- ✅ Sesiones en base de datos
- ✅ Todos los servicios estables
- ✅ Aplicación accesible externamente

## 📞 Soporte

Si encuentras algún problema, ejecuta:
```bash
# Diagnóstico completo
echo "=== DIAGNÓSTICO COMPLETO ===" > diagnostico.log
date >> diagnostico.log
docker-compose -f docker-compose.prod.yml ps >> diagnostico.log
docker-compose -f docker-compose.prod.yml logs --tail=50 web >> diagnostico.log
docker stats --no-stream >> diagnostico.log
df -h >> diagnostico.log

# Ver el diagnóstico
cat diagnostico.log
```