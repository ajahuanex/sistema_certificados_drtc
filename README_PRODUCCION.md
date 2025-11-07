# 🚀 Guía de Despliegue en Producción

## Sistema de Certificados DRTC - Configuración de Producción

---

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Configuración Inicial](#configuración-inicial)
3. [Despliegue Local (Pruebas)](#despliegue-local-pruebas)
4. [Despliegue en Servidor](#despliegue-en-servidor)
5. [Mantenimiento](#mantenimiento)
6. [Troubleshooting](#troubleshooting)

---

## 📦 Requisitos Previos

### Software Necesario:
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git

### Verificar instalación:
```bash
docker --version
docker compose version
git --version
```

---

## ⚙️ Configuración Inicial

### 1. Clonar el Repositorio
```bash
git clone <tu-repositorio>
cd certificados-drtc
```

### 2. Configurar Variables de Entorno

El archivo `.env.production` ya está configurado para pruebas locales.

**Para producción real, actualiza:**

```bash
# Copiar ejemplo
cp .env.production.example .env.production

# Editar con tus valores
nano .env.production
```

**Variables críticas a cambiar:**
```bash
# Seguridad
SECRET_KEY=genera-una-clave-aleatoria-muy-larga-y-segura

# Hosts permitidos
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# Base de datos (usa contraseñas fuertes)
DB_PASSWORD=contraseña-segura-postgresql

# SSL (solo si tienes HTTPS configurado)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## 🧪 Despliegue Local (Pruebas)

### Método 1: Script Automático (RECOMENDADO)

**Windows:**
```cmd
test-produccion-completo.bat
```

**Linux/Mac:**
```bash
chmod +x test-produccion-completo.sh
./test-produccion-completo.sh
```

### Método 2: Comandos Manuales

```bash
# 1. Construir imagen
docker compose -f docker-compose.prod.yml build

# 2. Iniciar servicios
docker compose -f docker-compose.prod.yml up -d

# 3. Ver logs
docker compose -f docker-compose.prod.yml logs -f

# 4. Verificar estado
docker compose -f docker-compose.prod.yml ps
```

### Acceder a la Aplicación:
- **Aplicación:** http://localhost
- **Admin:** http://localhost/admin/
- **Health Check:** http://localhost/health/

### Credenciales por Defecto:
```
Usuario: admin
Contraseña: admin123
```
⚠️ **CAMBIAR EN PRODUCCIÓN**

---

## 🌐 Despliegue en Servidor

### 1. Preparar el Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt install docker-compose-plugin -y

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
```

### 2. Configurar Firewall

```bash
# Permitir HTTP y HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. Clonar y Configurar

```bash
# Clonar repositorio
git clone <tu-repositorio>
cd certificados-drtc

# Configurar variables de entorno
cp .env.production.example .env.production
nano .env.production
```

### 4. Configurar SSL/HTTPS (Opcional pero Recomendado)

#### Opción A: Let's Encrypt con Certbot

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Copiar certificados a proyecto
sudo cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem ./ssl/
sudo cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem ./ssl/
sudo chown -R $USER:$USER ./ssl/
```

#### Opción B: Certificado Propio

```bash
# Crear directorio SSL
mkdir -p ssl

# Copiar tus certificados
cp tu-certificado.crt ssl/fullchain.pem
cp tu-clave-privada.key ssl/privkey.pem
```

**Actualizar nginx.prod.conf:**
```nginx
server {
    listen 443 ssl http2;
    server_name tu-dominio.com;
    
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    # ... resto de configuración
}
```

**Actualizar .env.production:**
```bash
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

### 5. Desplegar

```bash
# Construir e iniciar
docker compose -f docker-compose.prod.yml up -d --build

# Ver logs
docker compose -f docker-compose.prod.yml logs -f
```

### 6. Verificar Despliegue

```bash
# Estado de contenedores
docker compose -f docker-compose.prod.yml ps

# Health check
curl http://tu-dominio.com/health/

# Diagnóstico completo
./diagnostico-rapido.sh
```

---

## 🔧 Mantenimiento

### Ver Logs

```bash
# Todos los servicios
docker compose -f docker-compose.prod.yml logs -f

# Solo web
docker compose -f docker-compose.prod.yml logs -f web

# Solo base de datos
docker compose -f docker-compose.prod.yml logs -f db
```

### Backup de Base de Datos

```bash
# Backup manual
docker compose -f docker-compose.prod.yml exec db pg_dump -U certificados_user certificados_prod > backup_$(date +%Y%m%d).sql

# Backup automático (ya configurado)
docker compose -f docker-compose.prod.yml --profile backup up -d backup
```

### Restaurar Base de Datos

```bash
# Desde archivo SQL
docker compose -f docker-compose.prod.yml exec -T db psql -U certificados_user certificados_prod < backup.sql
```

### Actualizar Aplicación

```bash
# Método 1: Script automático
./update-production.sh

# Método 2: Manual
git pull
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

### Reiniciar Servicios

```bash
# Todos los servicios
docker compose -f docker-compose.prod.yml restart

# Solo web
docker compose -f docker-compose.prod.yml restart web

# Solo base de datos
docker compose -f docker-compose.prod.yml restart db
```

### Limpiar Recursos

```bash
# Detener y eliminar contenedores
docker compose -f docker-compose.prod.yml down

# Eliminar también volúmenes (⚠️ BORRA DATOS)
docker compose -f docker-compose.prod.yml down -v

# Limpiar imágenes no usadas
docker system prune -a
```

---

## 🐛 Troubleshooting

### Problema: Contenedor web no inicia

**Diagnóstico:**
```bash
docker compose -f docker-compose.prod.yml logs web
```

**Soluciones comunes:**
1. Verificar variables de entorno en `.env.production`
2. Verificar que PostgreSQL esté corriendo
3. Reconstruir imagen: `docker compose -f docker-compose.prod.yml build --no-cache web`

### Problema: Error de conexión a base de datos

**Diagnóstico:**
```bash
docker compose -f docker-compose.prod.yml exec web python manage.py dbshell
```

**Soluciones:**
1. Verificar `DB_PASSWORD` en `.env.production`
2. Verificar que contenedor db esté healthy: `docker compose -f docker-compose.prod.yml ps`
3. Revisar logs de PostgreSQL: `docker compose -f docker-compose.prod.yml logs db`

### Problema: Archivos estáticos no se cargan

**Solución:**
```bash
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker compose -f docker-compose.prod.yml restart nginx
```

### Problema: Error 502 Bad Gateway

**Diagnóstico:**
```bash
docker compose -f docker-compose.prod.yml logs nginx
docker compose -f docker-compose.prod.yml logs web
```

**Soluciones:**
1. Verificar que contenedor web esté corriendo
2. Verificar health check: `docker compose -f docker-compose.prod.yml ps`
3. Reiniciar nginx: `docker compose -f docker-compose.prod.yml restart nginx`

### Problema: Permisos de archivos

**Solución:**
```bash
# Ajustar permisos de directorios
sudo chown -R 1000:1000 media/ staticfiles/ logs/ backups/
```

### Script de Diagnóstico Rápido

```bash
# Windows
diagnostico-rapido.bat

# Linux/Mac
./diagnostico-rapido.sh
```

---

## 📊 Monitoreo

### Verificar Salud de Servicios

```bash
# Health checks
docker compose -f docker-compose.prod.yml ps

# Uso de recursos
docker stats
```

### Logs en Tiempo Real

```bash
# Todos los servicios
docker compose -f docker-compose.prod.yml logs -f

# Filtrar errores
docker compose -f docker-compose.prod.yml logs | grep -i error
```

### Métricas (Opcional)

Si habilitaste el servicio de monitoreo:
```bash
# Iniciar monitoreo
docker compose -f docker-compose.prod.yml --profile monitoring up -d monitoring

# Acceder a métricas
curl http://localhost:9100/metrics
```

---

## 🔐 Seguridad

### Checklist de Seguridad:

- [ ] SECRET_KEY único y aleatorio
- [ ] DEBUG=False en producción
- [ ] Contraseñas fuertes para DB_PASSWORD
- [ ] ALLOWED_HOSTS configurado correctamente
- [ ] SSL/HTTPS habilitado (si aplica)
- [ ] Firewall configurado
- [ ] Backups automáticos habilitados
- [ ] Credenciales de admin cambiadas
- [ ] Actualizaciones de seguridad aplicadas

### Generar SECRET_KEY Segura:

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 📚 Recursos Adicionales

### Documentación del Proyecto:
- `docs/PRODUCTION_DEPLOYMENT.md` - Guía detallada de despliegue
- `docs/ADMIN_GUIDE.md` - Guía de administración
- `SOLUCION_PRODUCCION_FINAL.md` - Solución de problemas comunes
- `CORRECCION_PRODUCCION_APLICADA.md` - Cambios recientes

### Comandos Útiles:
- `COMANDOS_RAPIDOS_PRODUCCION.md` - Referencia rápida
- `COMANDOS_TROUBLESHOOTING.md` - Comandos de diagnóstico

### Scripts Disponibles:
- `test-produccion-completo.bat/sh` - Prueba completa
- `diagnostico-rapido.bat/sh` - Diagnóstico rápido
- `update-production.bat/sh` - Actualización automática

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisa la sección [Troubleshooting](#troubleshooting)
2. Ejecuta el script de diagnóstico
3. Revisa los logs de los contenedores
4. Consulta la documentación en `docs/`

---

**Última actualización:** 2025-11-07  
**Versión:** 1.0  
**Estado:** ✅ Producción Ready
