# 🚀 GUÍA PASO A PASO PARA PRODUCCIÓN
## Como si fueras un niño de 5 años 👶

### 📋 **ANTES DE EMPEZAR - CHECKLIST**
- [ ] Tienes acceso a tu servidor (SSH o panel de control)
- [ ] Tu servidor tiene Ubuntu/Debian/CentOS
- [ ] Tienes permisos de administrador (sudo)
- [ ] Tienes conexión a internet en el servidor

---

## 🎯 **PASO 1: CONECTARTE A TU SERVIDOR**

### Si usas SSH (Terminal):
```bash
ssh tu_usuario@tu_servidor.com
# Ejemplo: ssh root@192.168.1.100
```

### Si usas panel web:
- Abre tu panel de control (cPanel, Plesk, etc.)
- Busca "Terminal" o "SSH"
- Haz clic para abrir

---

## 🛠️ **PASO 2: INSTALAR DOCKER (Si no lo tienes)**

### Para Ubuntu/Debian:
```bash
# 1. Actualizar el sistema
sudo apt update

# 2. Instalar Docker
sudo apt install -y docker.io docker-compose

# 3. Iniciar Docker
sudo systemctl start docker
sudo systemctl enable docker

# 4. Verificar que funciona
sudo docker --version
sudo docker-compose --version
```

### Para CentOS/RHEL:
```bash
# 1. Instalar Docker
sudo yum install -y docker docker-compose

# 2. Iniciar Docker
sudo systemctl start docker
sudo systemctl enable docker
```

---

## 📥 **PASO 3: DESCARGAR TU PROYECTO**

```bash
# 1. Ir a la carpeta donde quieres instalar
cd /home
# o
cd /var/www

# 2. Clonar tu proyecto desde GitHub
git clone https://github.com/ajahuanex/sistema_certificados_drtc.git

# 3. Entrar a la carpeta
cd sistema_certificados_drtc

# 4. Verificar que se descargó todo
ls -la
```

**Deberías ver archivos como:**
- `Dockerfile`
- `docker-compose.prod.yml`
- `requirements.txt`
- Carpeta `certificates/`

---

## ⚙️ **PASO 4: CONFIGURAR VARIABLES DE PRODUCCIÓN**

```bash
# 1. Copiar el archivo de ejemplo
cp .env.production.example .env.production

# 2. Editar el archivo (usa nano o vi)
nano .env.production
```

**Cambiar estas líneas IMPORTANTES:**
```env
# Cambiar por tu dominio real
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# Cambiar por una clave súper secreta (mínimo 50 caracteres)
SECRET_KEY=tu-clave-super-secreta-aqui-minimo-50-caracteres-123456789

# Configurar base de datos
DB_NAME=certificados_prod
DB_USER=postgres
DB_PASSWORD=tu-password-seguro
DB_HOST=db
DB_PORT=5432

# Email (opcional, para notificaciones)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password-email
```

**Para guardar en nano:**
- Presiona `Ctrl + X`
- Presiona `Y`
- Presiona `Enter`

---

## 🚀 **PASO 5: LEVANTAR EL SISTEMA**

```bash
# 1. Construir y levantar los contenedores
sudo docker-compose -f docker-compose.prod.yml up -d --build

# 2. Esperar a que termine (puede tomar 5-10 minutos)
# Verás muchas líneas de texto, es normal

# 3. Verificar que todo esté corriendo
sudo docker-compose -f docker-compose.prod.yml ps
```

**Deberías ver algo así:**
```
Name                    State    Ports
certificados_web_1      Up       0.0.0.0:80->80/tcp
certificados_db_1       Up       5432/tcp
certificados_nginx_1    Up       0.0.0.0:443->443/tcp
```

---

## 🔧 **PASO 6: CONFIGURAR LA BASE DE DATOS**

```bash
# 1. Ejecutar migraciones
sudo docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# 2. Crear superusuario
sudo docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Te preguntará:
# Username: admin
# Email: tu-email@ejemplo.com  
# Password: (escribe una contraseña segura)
# Password (again): (repite la contraseña)

# 3. Cargar plantilla por defecto
sudo docker-compose -f docker-compose.prod.yml exec web python manage.py load_default_template
```

---

## 🌐 **PASO 7: CONFIGURAR DOMINIO (Si tienes uno)**

### Si tienes dominio propio:
1. **En tu proveedor de dominio** (GoDaddy, Namecheap, etc.):
   - Crear registro A: `tu-dominio.com` → IP de tu servidor
   - Crear registro A: `www.tu-dominio.com` → IP de tu servidor

2. **Esperar 5-30 minutos** para que se propague

3. **Probar**: `http://tu-dominio.com`

### Si NO tienes dominio:
- Usar la IP directamente: `http://IP-DE-TU-SERVIDOR`
- Ejemplo: `http://192.168.1.100`

---

## ✅ **PASO 8: VERIFICAR QUE TODO FUNCIONA**

### 1. Probar la página principal:
```bash
# Desde el servidor
curl http://localhost

# Desde tu computadora
# Abrir navegador: http://tu-dominio.com o http://IP-SERVIDOR
```

### 2. Probar el admin:
- Ir a: `http://tu-dominio.com/admin/`
- Usar el usuario que creaste en el paso 6
- Deberías ver el panel de Django

### 3. Probar el sistema:
- Ir a: `http://tu-dominio.com/`
- Deberías ver la página de consulta de certificados

---

## 🔄 **PASO 9: CONFIGURAR ACTUALIZACIONES AUTOMÁTICAS**

```bash
# 1. Hacer ejecutable el script
chmod +x update-production.sh

# 2. Probar actualización manual
./update-production.sh

# 3. Configurar cron para actualizaciones automáticas (opcional)
crontab -e

# Agregar esta línea (actualizar cada día a las 3 AM):
0 3 * * * cd /ruta/a/tu/proyecto && ./update-production.sh >> /var/log/update-certificados.log 2>&1
```

---

## 🆘 **PASO 10: QUÉ HACER SI ALGO SALE MAL**

### Ver logs de errores:
```bash
# Ver logs del contenedor web
sudo docker-compose -f docker-compose.prod.yml logs web

# Ver logs de la base de datos
sudo docker-compose -f docker-compose.prod.yml logs db

# Ver logs de nginx
sudo docker-compose -f docker-compose.prod.yml logs nginx
```

### Reiniciar todo:
```bash
# Parar todo
sudo docker-compose -f docker-compose.prod.yml down

# Levantar todo de nuevo
sudo docker-compose -f docker-compose.prod.yml up -d
```

### Volver a una versión anterior:
```bash
# Ver commits disponibles
git log --oneline -10

# Volver a un commit específico
git checkout CODIGO-DEL-COMMIT

# Reconstruir
sudo docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🎉 **¡LISTO! TU SISTEMA ESTÁ EN PRODUCCIÓN**

### URLs importantes:
- **Página principal**: `http://tu-dominio.com/`
- **Admin**: `http://tu-dominio.com/admin/`
- **API**: `http://tu-dominio.com/api/`

### Credenciales:
- **Usuario admin**: El que creaste en el paso 6
- **Base de datos**: Configurada automáticamente

### Para futuras actualizaciones:
```bash
# Solo ejecutar esto:
./update-production.sh
```

---

## 📞 **CONTACTO DE EMERGENCIA**
Si algo no funciona:
1. Copia el error exacto
2. Ejecuta: `sudo docker-compose -f docker-compose.prod.yml logs`
3. Guarda el resultado
4. Contacta soporte con esa información

---

## 🔒 **SEGURIDAD BÁSICA (MUY IMPORTANTE)**

### 1. Cambiar puerto SSH (opcional pero recomendado):
```bash
sudo nano /etc/ssh/sshd_config
# Cambiar: Port 22 → Port 2222
sudo systemctl restart ssh
```

### 2. Configurar firewall:
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 2222/tcp  # Si cambiaste el puerto SSH
sudo ufw enable
```

### 3. Backup automático:
```bash
# Agregar a crontab
0 2 * * * cd /ruta/a/tu/proyecto && ./backup_database.sh
```

---

¡Eso es todo! 🎊 **Tu sistema está listo para producción.**