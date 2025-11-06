# 🔧 CÓMO CAMBIAR PUERTOS EN PRODUCCIÓN
## Si el puerto 80 ya está ocupado

### 🎯 **PROBLEMA COMÚN**
Si al ejecutar `docker-compose` ves este error:
```
ERROR: for nginx  Cannot start service nginx: driver failed programming external connectivity on endpoint certificados_nginx_prod: Bind for 0.0.0.0:80 failed: port is already allocated
```

**¡No te preocupes!** Es súper fácil de solucionar.

---

## 🔧 **SOLUCIÓN 1: CAMBIAR PUERTO HTTP (Más Común)**

### 1. Editar docker-compose.prod.yml
```bash
nano docker-compose.prod.yml
```

### 2. Buscar la sección de nginx:
```yaml
# ANTES (líneas 85-87 aproximadamente)
nginx:
  ports:
    - "80:80"
    - "443:443"
```

### 3. Cambiar por otro puerto (ejemplo: 8080):
```yaml
# DESPUÉS
nginx:
  ports:
    - "8080:80"    # ← CAMBIAR AQUÍ
    - "443:443"
```

### 4. Guardar y reiniciar:
```bash
# Guardar: Ctrl+X, Y, Enter
sudo docker-compose -f docker-compose.prod.yml down
sudo docker-compose -f docker-compose.prod.yml up -d
```

### 5. Acceder con el nuevo puerto:
```
http://tu-dominio.com:8080
http://IP-SERVIDOR:8080
```

---

## 🔧 **SOLUCIÓN 2: CAMBIAR AMBOS PUERTOS**

Si también el puerto 443 está ocupado:

```yaml
nginx:
  ports:
    - "8080:80"    # HTTP en puerto 8080
    - "8443:443"   # HTTPS en puerto 8443
```

**Acceso:**
- HTTP: `http://tu-dominio.com:8080`
- HTTPS: `https://tu-dominio.com:8443`

---

## 🔧 **SOLUCIÓN 3: USAR PUERTOS ALTERNATIVOS COMUNES**

### Opciones populares:
```yaml
# Opción A - Puertos 8000/8001
nginx:
  ports:
    - "8000:80"
    - "8001:443"

# Opción B - Puertos 3000/3001  
nginx:
  ports:
    - "3000:80"
    - "3001:443"

# Opción C - Puertos 9000/9001
nginx:
  ports:
    - "9000:80"
    - "9001:443"
```

---

## 🔧 **SOLUCIÓN 4: VERIFICAR QUÉ ESTÁ USANDO EL PUERTO**

### Ver qué proceso usa el puerto 80:
```bash
# En Linux/Ubuntu
sudo netstat -tlnp | grep :80
sudo lsof -i :80

# En Windows
netstat -ano | findstr :80
```

### Parar el servicio que usa el puerto (si es posible):
```bash
# Ejemplos comunes:
sudo systemctl stop apache2    # Apache
sudo systemctl stop nginx     # Nginx
sudo service httpd stop       # Apache en CentOS
```

---

## 🔧 **SOLUCIÓN 5: CONFIGURACIÓN COMPLETA PERSONALIZADA**

### Crear archivo docker-compose.custom.yml:
```yaml
# docker-compose.custom.yml
version: '3.8'

services:
  nginx:
    ports:
      - "8080:80"     # Tu puerto personalizado
      - "8443:443"    # Tu puerto HTTPS personalizado
    environment:
      - CUSTOM_PORT=8080
```

### Usar el archivo personalizado:
```bash
sudo docker-compose -f docker-compose.prod.yml -f docker-compose.custom.yml up -d
```

---

## 🌐 **ACTUALIZAR CONFIGURACIÓN DE NGINX**

Si cambias puertos, también actualiza `nginx.prod.conf`:

```bash
nano nginx.prod.conf
```

### Buscar y cambiar:
```nginx
# Si usas puerto personalizado, agregar:
server {
    listen 80;
    server_name _;
    
    # Redirigir a tu puerto personalizado si es necesario
    return 301 http://$host:8080$request_uri;
}
```

---

## 🔥 **COMANDOS RÁPIDOS PARA CAMBIO DE PUERTO**

### Script automático para cambiar a puerto 8080:
```bash
#!/bin/bash
echo "🔧 Cambiando puerto a 8080..."

# Backup del archivo original
cp docker-compose.prod.yml docker-compose.prod.yml.backup

# Cambiar puerto 80 por 8080
sed -i 's/"80:80"/"8080:80"/g' docker-compose.prod.yml

echo "✅ Puerto cambiado a 8080"
echo "🚀 Reiniciando servicios..."

sudo docker-compose -f docker-compose.prod.yml down
sudo docker-compose -f docker-compose.prod.yml up -d

echo "🎉 ¡Listo! Accede en: http://tu-servidor:8080"
```

### Guardar como cambiar_puerto.sh:
```bash
nano cambiar_puerto.sh
# Copiar el script de arriba
chmod +x cambiar_puerto.sh
./cambiar_puerto.sh
```

---

## 🆘 **SOLUCIÓN DE PROBLEMAS**

### Error: "Address already in use"
```bash
# Ver todos los puertos ocupados
sudo netstat -tlnp

# Matar proceso específico (cuidado!)
sudo kill -9 PID_DEL_PROCESO
```

### Error: "Permission denied"
```bash
# Usar puertos > 1024 (no requieren sudo)
nginx:
  ports:
    - "8080:80"   # ✅ Funciona sin sudo
    - "8443:443"  # ✅ Funciona sin sudo
```

### Verificar que el cambio funcionó:
```bash
# Ver puertos activos de Docker
sudo docker ps

# Probar conexión
curl http://localhost:8080
```

---

## 🎯 **PUERTOS RECOMENDADOS POR TIPO DE SERVIDOR**

### Servidor compartido (hosting):
```yaml
ports:
  - "8080:80"   # HTTP alternativo
  - "8443:443"  # HTTPS alternativo
```

### VPS/Servidor dedicado:
```yaml
ports:
  - "3000:80"   # Puerto común para apps
  - "3001:443"  # HTTPS correspondiente
```

### Desarrollo/Testing:
```yaml
ports:
  - "8000:80"   # Puerto de desarrollo Django
  - "8001:443"  # HTTPS de desarrollo
```

---

## 🔒 **CONFIGURAR FIREWALL CON NUEVO PUERTO**

```bash
# Permitir el nuevo puerto en firewall
sudo ufw allow 8080/tcp
sudo ufw allow 8443/tcp

# Verificar reglas
sudo ufw status
```

---

## 🎊 **¡LISTO! PUERTO CAMBIADO**

Después del cambio:

1. **✅ Reinicia los contenedores**
2. **✅ Verifica que funciona**: `http://tu-servidor:NUEVO_PUERTO`
3. **✅ Actualiza tus bookmarks/enlaces**
4. **✅ Informa a los usuarios del nuevo puerto**

### URLs finales:
- **Página principal**: `http://tu-dominio.com:8080/`
- **Admin**: `http://tu-dominio.com:8080/admin/`
- **API**: `http://tu-dominio.com:8080/api/`

**¡Tu sistema funciona perfectamente en el nuevo puerto!** 🚀