# ⚡ COMANDOS RÁPIDOS PARA PRODUCCIÓN
## Para copiar y pegar directamente

### 🚀 **INSTALACIÓN COMPLETA EN UN SOLO SCRIPT**

```bash
#!/bin/bash
# SCRIPT DE INSTALACIÓN AUTOMÁTICA

echo "🚀 Iniciando instalación del Sistema de Certificados DRTC..."

# 1. Actualizar sistema
echo "📦 Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

# 2. Instalar Docker
echo "🐳 Instalando Docker..."
sudo apt install -y docker.io docker-compose git curl

# 3. Iniciar Docker
echo "▶️ Iniciando Docker..."
sudo systemctl start docker
sudo systemctl enable docker

# 4. Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# 5. Descargar proyecto
echo "📥 Descargando proyecto..."
cd /home
git clone https://github.com/ajahuanex/sistema_certificados_drtc.git
cd sistema_certificados_drtc

# 6. Configurar variables de entorno
echo "⚙️ Configurando variables..."
cp .env.production.example .env.production

echo "✅ Instalación base completada!"
echo "🔧 Ahora debes:"
echo "1. Editar .env.production con tus datos"
echo "2. Ejecutar: sudo docker-compose -f docker-compose.prod.yml up -d --build"
echo "3. Configurar la base de datos"
```

### 💾 **GUARDAR COMO install.sh**
```bash
# Crear el archivo
nano install.sh

# Copiar el script de arriba
# Guardar: Ctrl+X, Y, Enter

# Hacer ejecutable
chmod +x install.sh

# Ejecutar
./install.sh
```

---

### ⚙️ **CONFIGURACIÓN RÁPIDA .env.production**

```bash
# COPIAR Y PEGAR EN .env.production
DEBUG=False
SECRET_KEY=CAMBIAR-POR-CLAVE-SUPER-SECRETA-MINIMO-50-CARACTERES-123456789
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com,localhost,127.0.0.1

# Base de datos
DB_NAME=certificados_prod
DB_USER=postgres
DB_PASSWORD=password123
DB_HOST=db
DB_PORT=5432

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password

# Configuración adicional
TIME_ZONE=America/Lima
LANGUAGE_CODE=es-pe
```

---

### 🚀 **LEVANTAR SISTEMA (COMANDOS EXACTOS)**

```bash
# 1. Ir a la carpeta del proyecto
cd /home/sistema_certificados_drtc

# 2. Levantar contenedores
sudo docker-compose -f docker-compose.prod.yml up -d --build

# 3. Esperar 2-3 minutos, luego verificar
sudo docker-compose -f docker-compose.prod.yml ps

# 4. Configurar base de datos
sudo docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# 5. Crear superusuario
sudo docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# 6. Cargar plantilla por defecto
sudo docker-compose -f docker-compose.prod.yml exec web python manage.py load_default_template

# 7. Verificar que funciona
curl http://localhost
```

---

### 🔧 **COMANDOS DE MANTENIMIENTO**

```bash
# Ver logs en tiempo real
sudo docker-compose -f docker-compose.prod.yml logs -f

# Ver logs específicos
sudo docker-compose -f docker-compose.prod.yml logs web
sudo docker-compose -f docker-compose.prod.yml logs db
sudo docker-compose -f docker-compose.prod.yml logs nginx

# Reiniciar servicios
sudo docker-compose -f docker-compose.prod.yml restart

# Parar todo
sudo docker-compose -f docker-compose.prod.yml down

# Levantar todo
sudo docker-compose -f docker-compose.prod.yml up -d

# Actualizar desde GitHub
git pull origin main
sudo docker-compose -f docker-compose.prod.yml up -d --build

# Backup de base de datos
sudo docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres certificados_prod > backup_$(date +%Y%m%d).sql
```

---

### 🆘 **COMANDOS DE EMERGENCIA**

```bash
# Si algo no funciona - RESET COMPLETO
sudo docker-compose -f docker-compose.prod.yml down -v
sudo docker system prune -a -f
git pull origin main
sudo docker-compose -f docker-compose.prod.yml up -d --build

# Ver espacio en disco
df -h

# Ver memoria RAM
free -h

# Ver procesos de Docker
sudo docker ps -a

# Entrar al contenedor web
sudo docker-compose -f docker-compose.prod.yml exec web bash

# Entrar a la base de datos
sudo docker-compose -f docker-compose.prod.yml exec db psql -U postgres certificados_prod
```

---

### 🔒 **CONFIGURACIÓN DE SEGURIDAD BÁSICA**

```bash
# Configurar firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Cambiar puerto SSH (opcional)
sudo nano /etc/ssh/sshd_config
# Cambiar: Port 22 → Port 2222
sudo systemctl restart ssh

# Configurar actualizaciones automáticas
echo "0 3 * * * cd /home/sistema_certificados_drtc && ./update-production.sh" | crontab -
```

---

### 📊 **VERIFICACIÓN RÁPIDA**

```bash
# Verificar que todo funciona
echo "🔍 Verificando servicios..."

# 1. Docker corriendo
sudo docker ps

# 2. Puertos abiertos
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# 3. Respuesta HTTP
curl -I http://localhost

# 4. Logs sin errores
sudo docker-compose -f docker-compose.prod.yml logs --tail=50

echo "✅ Verificación completada"
```

---

### 🎯 **URLS IMPORTANTES**

```bash
# Después de la instalación, probar estas URLs:

# Página principal
http://tu-dominio.com/
http://IP-DEL-SERVIDOR/

# Panel de administración
http://tu-dominio.com/admin/
http://IP-DEL-SERVIDOR/admin/

# API
http://tu-dominio.com/api/
http://IP-DEL-SERVIDOR/api/

# Consulta de certificados
http://tu-dominio.com/consultar/
http://IP-DEL-SERVIDOR/consultar/
```

---

### 📱 **COMANDOS DESDE TU CELULAR/TABLET**

Si necesitas administrar desde móvil, usa una app SSH como:
- **Termius** (iOS/Android)
- **JuiceSSH** (Android)
- **Prompt 3** (iOS)

Comandos básicos para móvil:
```bash
# Ver estado
sudo docker ps

# Ver logs
sudo docker logs certificados_web_1

# Reiniciar
sudo docker restart certificados_web_1
```

---

## 🎊 **¡LISTO PARA PRODUCCIÓN!**

Con estos comandos tienes todo lo necesario para:
- ✅ Instalar el sistema
- ✅ Configurarlo correctamente  
- ✅ Mantenerlo funcionando
- ✅ Solucionar problemas
- ✅ Hacer actualizaciones

**¡Tu sistema de certificados está listo para el mundo real!** 🚀