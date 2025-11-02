# 🐳 Docker - Sistema de Certificados DRTC

## 🚀 Inicio Rápido

### Para Desarrollo
```bash
# Linux/Mac
./start-dev.sh

# Windows
start-dev.bat
```

### Para Producción
```bash
# Configurar variables de entorno
cp .env.production.example .env.production
nano .env.production  # Editar valores

# Desplegar
docker-compose -f docker-compose.prod.yml up -d

# Actualizar desde GitHub
./update-production.sh
```

## 📁 Estructura de Archivos Docker

```
proyecto/
├── Dockerfile                 # Imagen principal de Django
├── .dockerignore             # Archivos excluidos del build
├── docker-compose.yml        # Desarrollo
├── docker-compose.prod.yml   # Producción
├── nginx.prod.conf           # Configuración Nginx
├── .env.production.example   # Variables de entorno
├── start-dev.sh             # Script inicio desarrollo
├── start-dev.bat            # Script inicio Windows
├── update-production.sh     # Script actualización
└── update-production.bat    # Script actualización Windows
```

## 🔧 Comandos Útiles

### Desarrollo
```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f web

# Ejecutar comandos Django
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic
docker-compose exec web python manage.py createsuperuser

# Acceder al contenedor
docker-compose exec web bash

# Detener servicios
docker-compose down

# Reconstruir imagen
docker-compose build --no-cache web
```

### Producción
```bash
# Iniciar servicios de producción
docker-compose -f docker-compose.prod.yml up -d

# Ver estado
docker-compose -f docker-compose.prod.yml ps

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f web

# Backup de base de datos
docker-compose -f docker-compose.prod.yml exec db pg_dump -U certificados_user certificados_prod > backup.sql

# Actualizar sistema
./update-production.sh
```

## 🌐 Puertos y Servicios

### Desarrollo
- **Aplicación Django**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Adminer**: http://localhost:8080

### Producción
- **Aplicación (HTTP)**: http://localhost:80
- **Aplicación (HTTPS)**: https://localhost:443
- **PostgreSQL**: Solo interno (no expuesto)
- **Redis**: Solo interno (no expuesto)

## 🔒 Seguridad

### Variables de Entorno Críticas
```bash
# CAMBIAR OBLIGATORIAMENTE en producción:
SECRET_KEY=tu_secret_key_unico_y_seguro
DB_PASSWORD=password_super_seguro
EMAIL_HOST_PASSWORD=tu_app_password
ALLOWED_HOSTS=tu-dominio.com
```

### Certificados SSL
```bash
# Colocar certificados en:
ssl/cert.pem    # Certificado público
ssl/key.pem     # Clave privada
```

## 📊 Monitoreo

### Health Checks
```bash
# Verificar salud de la aplicación
curl http://localhost/health/

# Verificar servicios Docker
docker-compose ps
```

### Logs
```bash
# Logs de la aplicación
docker-compose logs web

# Logs de Nginx
docker-compose logs nginx

# Logs de PostgreSQL
docker-compose logs db

# Todos los logs
docker-compose logs
```

## 🔄 Actualizaciones

### Flujo de Actualización
1. **Desarrollo local** → Push a GitHub
2. **En servidor**: Ejecutar `./update-production.sh`
3. **Script automático**:
   - Crea backup de BD
   - Descarga código nuevo
   - Reconstruye contenedores
   - Ejecuta migraciones
   - Verifica funcionamiento

### Rollback
```bash
# Rollback manual
git reset --hard HEAD~1
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# Restaurar backup de BD (si es necesario)
docker-compose -f docker-compose.prod.yml exec -T db psql -U certificados_user -d certificados_prod < backup.sql
```

## 🛠️ Troubleshooting

### Problemas Comunes

#### 1. Puerto ya en uso
```bash
# Ver qué proceso usa el puerto
sudo lsof -i :8000

# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Usar puerto 8001 en lugar de 8000
```

#### 2. Permisos de archivos
```bash
# Arreglar permisos
sudo chown -R $USER:$USER media/ staticfiles/ logs/
chmod 755 media/ staticfiles/ logs/
```

#### 3. Base de datos no conecta
```bash
# Verificar estado de PostgreSQL
docker-compose exec db pg_isready

# Reiniciar servicio de BD
docker-compose restart db
```

#### 4. Imagen no se construye
```bash
# Limpiar cache de Docker
docker system prune -a

# Reconstruir sin cache
docker-compose build --no-cache
```

## 📈 Optimización

### Para Desarrollo
- Usar volúmenes para hot-reload
- Habilitar DEBUG=True
- Usar SQLite si no necesitas PostgreSQL

### Para Producción
- Usar multi-stage builds
- Optimizar configuración de Nginx
- Configurar límites de recursos
- Habilitar compresión gzip

## 🔗 Enlaces Útiles

- [Documentación Docker](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Django Deployment](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Nginx Configuration](https://nginx.org/en/docs/)

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs: `docker-compose logs`
2. Verifica la configuración: `docker-compose config`
3. Consulta esta documentación
4. Contacta al equipo de desarrollo

---

**¡Tu aplicación está lista para funcionar con Docker!** 🐳🚀