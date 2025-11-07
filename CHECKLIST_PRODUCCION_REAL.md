# ✅ CHECKLIST PARA PRODUCCIÓN REAL

## 🎯 ESTADO ACTUAL
- ✅ Sistema funcionando 100% en local
- ✅ Todos los contenedores operativos
- ✅ Base de datos configurada
- ⚠️ **FALTA configuración de seguridad para producción**

---

## 🔒 TAREAS OBLIGATORIAS ANTES DE PRODUCCIÓN

### 1. SEGURIDAD CRÍTICA (OBLIGATORIO)

#### 1.1 Cambiar SECRET_KEY
```bash
# En .env.production, cambiar esta línea:
SECRET_KEY=clave-temporal-para-desarrollo-y-pruebas-locales-123456789-cambiar-en-produccion-real

# Por una clave segura generada:
SECRET_KEY=tu-clave-super-secreta-y-larga-generada-aleatoriamente-aqui
```

**Generar clave segura:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### 1.2 Cambiar Contraseña de Base de Datos
```bash
# En .env.production, cambiar:
DB_PASSWORD=certificados_password_123

# Por una contraseña fuerte:
DB_PASSWORD=TuContraseñaSuperSegura2025!@#
```

#### 1.3 Configurar Dominio Real
```bash
# En .env.production, actualizar:
ALLOWED_HOSTS=certificados.drtc.gob.pe,www.certificados.drtc.gob.pe
SITE_URL=https://certificados.drtc.gob.pe
```

#### 1.4 Habilitar SSL/HTTPS
```bash
# En .env.production, cambiar a True:
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

---

### 2. CERTIFICADO SSL (OBLIGATORIO)

#### Opción A: Let's Encrypt (GRATIS - Recomendado)
```bash
# 1. Instalar certbot en el servidor
sudo apt-get install certbot

# 2. Obtener certificado
sudo certbot certonly --standalone -d certificados.drtc.gob.pe

# 3. Copiar certificados a la carpeta ssl/
mkdir -p ssl
sudo cp /etc/letsencrypt/live/certificados.drtc.gob.pe/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/certificados.drtc.gob.pe/privkey.pem ssl/key.pem
```

#### Opción B: Certificado Comercial
- Comprar certificado SSL
- Colocar archivos en `ssl/cert.pem` y `ssl/key.pem`

#### Después de obtener certificados:
```bash
# Descomentar configuración HTTPS en nginx.prod.conf
# Buscar las líneas que empiezan con # server {
# y quitar los comentarios (#)
```

---

### 3. CREAR SUPERUSUARIO

```bash
# Opción A: Con variable de entorno
export DJANGO_SUPERUSER_PASSWORD="TuContraseñaSegura123!"
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser --noinput --username admin --email admin@drtc.gob.pe

# Opción B: Interactivo
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

---

### 4. CONFIGURAR DNS

En tu proveedor de DNS (donde está registrado drtc.gob.pe):

```
Tipo    Nombre                      Valor                   TTL
A       certificados.drtc.gob.pe    [IP_DE_TU_SERVIDOR]    3600
CNAME   www.certificados.drtc.gob.pe certificados.drtc.gob.pe 3600
```

---

### 5. CONFIGURAR FIREWALL EN SERVIDOR

```bash
# Permitir solo puertos necesarios
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

---

## 📋 CHECKLIST PASO A PASO

### Antes de Subir al Servidor

- [ ] ✅ Generar SECRET_KEY seguro
- [ ] ✅ Cambiar DB_PASSWORD
- [ ] ✅ Actualizar ALLOWED_HOSTS con dominio real
- [ ] ✅ Actualizar SITE_URL con https://
- [ ] ✅ Commit y push a GitHub

### En el Servidor de Producción

- [ ] ✅ Instalar Docker y Docker Compose
- [ ] ✅ Clonar repositorio desde GitHub
- [ ] ✅ Copiar .env.production con valores seguros
- [ ] ✅ Obtener certificado SSL
- [ ] ✅ Configurar nginx.prod.conf (descomentar HTTPS)
- [ ] ✅ Configurar DNS
- [ ] ✅ Construir imágenes: `docker compose -f docker-compose.prod.yml build`
- [ ] ✅ Iniciar servicios: `docker compose -f docker-compose.prod.yml up -d`
- [ ] ✅ Crear superusuario
- [ ] ✅ Verificar que todo funciona: `curl https://certificados.drtc.gob.pe/health/`

### Después del Despliegue

- [ ] ✅ Probar login en /admin/
- [ ] ✅ Probar generación de certificados
- [ ] ✅ Configurar backups automáticos
- [ ] ✅ Configurar monitoreo

---

## 🚀 COMANDOS PARA DESPLEGAR EN SERVIDOR

### 1. Preparar Servidor (Ubuntu/Debian)
```bash
# Actualizar sistema
sudo apt-get update && sudo apt-get upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt-get install docker-compose-plugin -y

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
```

### 2. Clonar y Configurar
```bash
# Clonar repositorio
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO

# Crear archivo .env.production con valores seguros
nano .env.production
# (Pegar contenido con valores seguros)

# Crear carpeta para SSL
mkdir -p ssl
```

### 3. Obtener Certificado SSL
```bash
# Instalar certbot
sudo apt-get install certbot -y

# Obtener certificado
sudo certbot certonly --standalone -d certificados.drtc.gob.pe

# Copiar certificados
sudo cp /etc/letsencrypt/live/certificados.drtc.gob.pe/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/certificados.drtc.gob.pe/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/*.pem
```

### 4. Descomentar HTTPS en nginx.prod.conf
```bash
# Editar nginx.prod.conf
nano nginx.prod.conf

# Buscar las líneas comentadas que empiezan con:
# # server {
# #     listen 443 ssl http2;

# Y quitar los comentarios (#) de toda esa sección
```

### 5. Desplegar
```bash
# Construir imágenes
docker compose -f docker-compose.prod.yml build --no-cache

# Iniciar servicios
docker compose -f docker-compose.prod.yml up -d

# Ver logs
docker compose -f docker-compose.prod.yml logs -f

# Crear superusuario
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### 6. Verificar
```bash
# Health check
curl https://certificados.drtc.gob.pe/health/

# Debe responder: {"status": "healthy"}
```

---

## ⚠️ IMPORTANTE: NO USAR EN PRODUCCIÓN SIN ESTOS CAMBIOS

**El sistema actual tiene configuración de DESARROLLO:**
- ❌ SECRET_KEY temporal
- ❌ Contraseña de BD débil
- ❌ Sin SSL/HTTPS
- ❌ Sin certificados

**Usar así en producción es un RIESGO DE SEGURIDAD GRAVE**

---

## 🎯 RESUMEN

### ¿Está listo para producción?
**NO** - Necesita configuración de seguridad

### ¿Qué falta?
1. Cambiar SECRET_KEY y DB_PASSWORD
2. Obtener certificado SSL
3. Configurar HTTPS en nginx
4. Configurar DNS
5. Crear superusuario seguro

### ¿Cuánto tiempo toma?
- **Con Let's Encrypt:** 30-60 minutos
- **Con certificado comercial:** 1-2 horas (depende de la compra)

### ¿Es difícil?
**NO** - Solo seguir los pasos de este checklist

---

## 📞 AYUDA

Si necesitas ayuda con algún paso:
1. Revisa la documentación en `docs/PRODUCTION_DEPLOYMENT.md`
2. Consulta `GUIA_PRODUCCION_PASO_A_PASO.md`
3. Revisa los logs: `docker compose -f docker-compose.prod.yml logs`

---

**Fecha:** 2025-11-07  
**Estado:** Sistema funcional en local, pendiente configuración de seguridad para producción  
**Próximo paso:** Configurar seguridad y SSL antes de desplegar
