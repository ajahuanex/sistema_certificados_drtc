# 🖥️ Comandos para Servidor Remoto - 161.132.47.92

## 🔐 PASO 1: Conectar al Servidor

```bash
ssh root@161.132.47.92
```

## 📁 PASO 2: Navegar al Proyecto

```bash
cd /root/sistema-certificados-drtc
```

## 🚀 PASO 3: Ejecutar Despliegue Automático

### Opción A: Comando Único (Recomendado)
```bash
curl -sSL https://raw.githubusercontent.com/tu-usuario/sistema-certificados-drtc/main/desplegar-remoto-sin-redis.sh | bash
```

### Opción B: Descargar y Ejecutar
```bash
# Descargar script
wget https://raw.githubusercontent.com/tu-usuario/sistema-certificados-drtc/main/desplegar-remoto-sin-redis.sh

# Dar permisos
chmod +x desplegar-remoto-sin-redis.sh

# Ejecutar
./desplegar-remoto-sin-redis.sh
```

### Opción C: Comandos Manuales Paso a Paso

#### 1. Actualizar código
```bash
git fetch origin
git reset --hard origin/main
git pull origin main
```

#### 2. Detener servicios
```bash
docker-compose -f docker-compose.prod.yml down
```

#### 3. Limpiar y construir
```bash
docker container prune -f
docker image prune -f
docker-compose -f docker-compose.prod.yml build --no-cache web
```

#### 4. Iniciar servicios (SIN Redis)
```bash
docker-compose -f docker-compose.prod.yml up -d db nginx web
```

#### 5. Configurar Django
```bash
# Esperar 30 segundos
sleep 30

# Migraciones
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Superusuario
docker-compose -f docker-compose.prod.yml exec web python manage.py create_superuser_if_not_exists

# Archivos estáticos
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Plantilla por defecto
docker-compose -f docker-compose.prod.yml exec web python manage.py load_default_template
```

#### 6. Verificar funcionamiento
```bash
# Estado de servicios
docker-compose -f docker-compose.prod.yml ps

# Logs de la aplicación
docker-compose -f docker-compose.prod.yml logs --tail=20 web

# Probar cache
docker-compose -f docker-compose.prod.yml exec web python -c "
from django.core.cache import cache
cache.set('test', 'ok', 60)
print('Cache test:', cache.get('test'))
"

# Probar conectividad
curl -I http://localhost:7070
curl -I http://161.132.47.92:7070
```

## ✅ Verificación Final

### URLs a probar desde tu navegador:
- **Principal**: http://161.132.47.92:7070
- **Admin**: http://161.132.47.92:7070/admin/
- **Credenciales**: admin / admin123

### Funcionalidades a verificar:
1. ✅ Página principal carga correctamente
2. ✅ Login en panel de administración
3. ✅ Dashboard de estadísticas
4. ✅ Importación de participantes
5. ✅ Generación de certificados
6. ✅ Consulta pública

## 📊 Monitoreo Continuo

### Ver logs en tiempo real:
```bash
docker-compose -f docker-compose.prod.yml logs -f web
```

### Ver estado de servicios:
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Ver uso de recursos:
```bash
docker stats
```

## 🔧 Troubleshooting

### Si hay problemas, ejecutar diagnóstico:
```bash
echo "=== DIAGNÓSTICO COMPLETO ===" > diagnostico.log
date >> diagnostico.log
docker-compose -f docker-compose.prod.yml ps >> diagnostico.log
docker-compose -f docker-compose.prod.yml logs --tail=50 web >> diagnostico.log
docker stats --no-stream >> diagnostico.log
df -h >> diagnostico.log
cat diagnostico.log
```

### Reiniciar servicios si es necesario:
```bash
docker-compose -f docker-compose.prod.yml restart web
docker-compose -f docker-compose.prod.yml restart nginx
```

### Verificar configuración de cache:
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py shell -c "
from django.conf import settings
print('USE_REDIS:', getattr(settings, 'USE_REDIS', 'No definido'))
print('Cache Backend:', settings.CACHES['default']['BACKEND'])
print('Session Engine:', settings.SESSION_ENGINE)
"
```

## 🎯 Resultado Esperado

Al finalizar, deberías tener:

- ✅ Sistema funcionando en http://161.132.47.92:7070
- ✅ Cache en memoria (sin Redis)
- ✅ Sesiones en base de datos PostgreSQL
- ✅ Todos los servicios estables
- ✅ Aplicación completamente funcional

## 📞 Soporte

Si necesitas ayuda adicional, proporciona:
1. Salida del comando `docker-compose -f docker-compose.prod.yml ps`
2. Logs: `docker-compose -f docker-compose.prod.yml logs --tail=50 web`
3. Resultado de: `curl -I http://161.132.47.92:7070`