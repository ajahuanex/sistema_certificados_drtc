# 🚀 Guía Completa de Despliegue Remoto

## 📋 Índice

1. [Requisitos Previos](#requisitos-previos)
2. [Subir a GitHub](#subir-a-github)
3. [Preparar Servidor Ubuntu](#preparar-servidor-ubuntu)
4. [Desplegar con Docker](#desplegar-con-docker)
5. [Configurar Dominio y SSL](#configurar-dominio-y-ssl)
6. [Verificación Post-Despliegue](#verificación-post-despliegue)
7. [Troubleshooting](#troubleshooting)

---

## 1. Requisitos Previos

### En tu Máquina Local (Windows)
- ✅ Git instalado
- ✅ Cuenta de GitHub
- ✅ Código probado localmente

### En el Servidor Remoto (Ubuntu)
- ✅ Ubuntu 20.04 o superior
- ✅ Acceso SSH (usuario con sudo)
- ✅ Puertos 80 y 443 abiertos
- ✅ Dominio apuntando al servidor (opcional pero recomendado)

### Información que Necesitarás
- IP del servidor: `_______________`
- Usuario SSH: `_______________`
- Dominio (opcional): `_______________`
- Email para SSL: `_______________`

---

## 2. Subir a GitHub

### Opción A: Script Automatizado (Recomendado)

```cmd
SUBIR_A_GITHUB_AHORA.bat
```

Este script:
- ✅ Verifica que Git esté instalado
- ✅ Inicializa el repositorio si es necesario
- ✅ Agrega todos los archivos
- ✅ Crea el commit
- ✅ Configura el remote
- ✅ Sube los cambios a GitHub

### Opción B: Comandos Manuales

```bash
# 1. Inicializar repositorio (si no existe)
git init

# 2. Agregar archivos
git add .

# 3. Crear commit
git commit -m "feat: Sistema completo de certificados con pruebas y despliegue"

# 4. Agregar repositorio remoto
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git

# 5. Subir cambios
git push -u origin main
```

### Verificar en GitHub

1. Ve a tu repositorio en GitHub
2. Verifica que todos los archivos estén presentes
3. Revisa que el README.md se vea correctamente

---

## 3. Preparar Servidor Ubuntu

### 3.1 Conectarse al Servidor

```bash
ssh usuario@IP_DEL_SERVIDOR
```

### 3.2 Actualizar Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 3.3 Instalar Docker y Docker Compose

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker --version
docker-compose --version

# Cerrar sesión y volver a conectar para aplicar cambios de grupo
exit
ssh usuario@IP_DEL_SERVIDOR
```

### 3.4 Instalar Git (si no está instalado)

```bash
sudo apt install git -y
git --version
```

---

## 4. Desplegar con Docker

### 4.1 Clonar Repositorio

```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/TU_REPO.git

# Entrar al directorio
cd TU_REPO
```

### 4.2 Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.production.example .env.production

# Editar variables de entorno
nano .env.production
```

**Variables importantes a configurar:**

```bash
# Django
SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com,IP_DEL_SERVIDOR

# Base de datos
POSTGRES_DB=certificados_db
POSTGRES_USER=certificados_user
POSTGRES_PASSWORD=tu-password-seguro-aqui

# Redis
REDIS_PASSWORD=tu-password-redis-aqui

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password-app

# Dominio
DOMAIN=tu-dominio.com
SSL_EMAIL=tu-email@gmail.com
```

**Generar SECRET_KEY seguro:**

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4.3 Dar Permisos a Scripts

```bash
chmod +x deploy-ubuntu.sh
chmod +x scripts/*.sh
chmod +x *.sh
```

### 4.4 Ejecutar Despliegue

```bash
./deploy-ubuntu.sh
```

Este script automáticamente:
- ✅ Verifica requisitos
- ✅ Construye las imágenes Docker
- ✅ Inicia los contenedores
- ✅ Ejecuta migraciones
- ✅ Recolecta archivos estáticos
- ✅ Crea superusuario
- ✅ Genera datos de prueba (opcional)

### 4.5 Verificar Contenedores

```bash
# Ver contenedores corriendo
docker-compose ps

# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f postgres
```

---

## 5. Configurar Dominio y SSL

### 5.1 Configurar DNS

En tu proveedor de dominio, crea estos registros:

```
Tipo    Nombre    Valor              TTL
A       @         IP_DEL_SERVIDOR    3600
A       www       IP_DEL_SERVIDOR    3600
```

### 5.2 Esperar Propagación DNS

```bash
# Verificar que el dominio apunte al servidor
nslookup tu-dominio.com
ping tu-dominio.com
```

### 5.3 Generar Certificado SSL con Let's Encrypt

```bash
# Opción A: Script automatizado
./scripts/generate-ssl-cert.sh

# Opción B: Manual con certbot
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

### 5.4 Configurar Renovación Automática

```bash
# Verificar que la renovación automática esté configurada
sudo certbot renew --dry-run

# El cron job se crea automáticamente, pero puedes verificar:
sudo crontab -l
```

---

## 6. Verificación Post-Despliegue

### 6.1 Verificar Servicios

```bash
# Estado de contenedores
docker-compose ps

# Salud de la aplicación
curl http://localhost/health/

# Verificar base de datos
docker-compose exec web python manage.py check --database default

# Verificar Redis
docker-compose exec redis redis-cli ping
```

### 6.2 Probar en Navegador

Abre tu navegador y verifica:

1. **Página principal:** https://tu-dominio.com
2. **Admin:** https://tu-dominio.com/admin/
   - Usuario: `admin`
   - Contraseña: `admin123` (cámbiala inmediatamente)
3. **Dashboard:** https://tu-dominio.com/admin/dashboard/
4. **Consulta pública:** https://tu-dominio.com/consulta/

### 6.3 Verificar SSL

```bash
# Verificar certificado SSL
curl -I https://tu-dominio.com

# Verificar en navegador
# Debe mostrar el candado verde y certificado válido
```

### 6.4 Cambiar Contraseña de Admin

```bash
docker-compose exec web python manage.py changepassword admin
```

---

## 7. Troubleshooting

### Problema: Contenedores no inician

```bash
# Ver logs detallados
docker-compose logs

# Reiniciar contenedores
docker-compose down
docker-compose up -d

# Reconstruir imágenes
docker-compose build --no-cache
docker-compose up -d
```

### Problema: Error de base de datos

```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps postgres

# Ver logs de PostgreSQL
docker-compose logs postgres

# Ejecutar migraciones manualmente
docker-compose exec web python manage.py migrate
```

### Problema: Archivos estáticos no cargan

```bash
# Recolectar archivos estáticos
docker-compose exec web python manage.py collectstatic --noinput

# Verificar permisos
docker-compose exec web ls -la /app/staticfiles

# Reiniciar nginx
docker-compose restart nginx
```

### Problema: SSL no funciona

```bash
# Verificar configuración de nginx
docker-compose exec nginx nginx -t

# Regenerar certificado
sudo certbot --nginx -d tu-dominio.com --force-renewal

# Verificar que el dominio apunte al servidor
nslookup tu-dominio.com
```

### Problema: No puedo acceder al admin

```bash
# Recrear superusuario
docker-compose exec web python manage.py create_superuser_if_not_exists --update --noinput

# O crear uno nuevo
docker-compose exec web python manage.py createsuperuser
```

### Problema: Puerto 80/443 ocupado

```bash
# Ver qué está usando el puerto
sudo lsof -i :80
sudo lsof -i :443

# Detener servicio que esté usando el puerto
sudo systemctl stop apache2  # Si Apache está instalado
sudo systemctl stop nginx    # Si nginx está instalado fuera de Docker
```

---

## 📊 Comandos Útiles

### Gestión de Contenedores

```bash
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Reiniciar servicios
docker-compose restart

# Ver logs en tiempo real
docker-compose logs -f

# Ejecutar comando en contenedor
docker-compose exec web python manage.py [comando]
```

### Backups

```bash
# Backup de base de datos
docker-compose exec postgres pg_dump -U certificados_user certificados_db > backup_$(date +%Y%m%d).sql

# Backup de archivos media
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/

# Restaurar base de datos
docker-compose exec -T postgres psql -U certificados_user certificados_db < backup_20250117.sql
```

### Actualizaciones

```bash
# Actualizar código desde GitHub
git pull origin main

# Reconstruir y reiniciar
docker-compose build
docker-compose up -d

# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Recolectar estáticos
docker-compose exec web python manage.py collectstatic --noinput
```

---

## 🎯 Checklist de Despliegue

Marca cada paso completado:

- [ ] Código subido a GitHub
- [ ] Servidor Ubuntu preparado
- [ ] Docker y Docker Compose instalados
- [ ] Repositorio clonado en servidor
- [ ] Variables de entorno configuradas
- [ ] Script de despliegue ejecutado
- [ ] Contenedores corriendo correctamente
- [ ] Base de datos funcionando
- [ ] Archivos estáticos cargando
- [ ] Admin accesible
- [ ] DNS configurado (si aplica)
- [ ] SSL configurado (si aplica)
- [ ] Contraseña de admin cambiada
- [ ] Backup configurado
- [ ] Monitoreo configurado

---

## 📚 Documentación Adicional

- **GUIA_DESPLIEGUE_PRODUCCION_2025.md** - Guía detallada de producción
- **DOCKER_README.md** - Documentación de Docker
- **docs/PRODUCTION_DEPLOYMENT.md** - Deployment avanzado
- **COMANDOS_RAPIDOS_PRODUCCION.md** - Comandos útiles

---

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs: `docker-compose logs`
2. Consulta la sección de Troubleshooting
3. Revisa la documentación adicional
4. Verifica que todas las variables de entorno estén configuradas

---

**¡Felicidades! Tu sistema de certificados está desplegado en producción.** 🎉
