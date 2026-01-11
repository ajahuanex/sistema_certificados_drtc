# 🌐 CONFIGURACIÓN NGINX PROXY MANAGER PARA CERTIFICADOS DRTC

## 📋 SITUACIÓN ACTUAL

- ✅ **Aplicación funcionando**: Puerto 7070 (interno)
- ✅ **Nginx Proxy Manager**: Puertos 80/443 (público)
- ✅ **Dominio configurado**: certificados.transportespuno.gob.pe → IP 161.132.47.99
- ❌ **Falta**: Configurar proxy reverso en NPM

---

## 🔧 PASOS PARA CONFIGURAR NGINX PROXY MANAGER

### 1. Acceder a Nginx Proxy Manager
```
URL: http://161.132.47.99:8090
Usuario: admin@example.com (por defecto)
Contraseña: changeme (por defecto)
```

### 2. Crear Proxy Host
1. **Ir a**: `Proxy Hosts` → `Add Proxy Host`

2. **Configurar pestaña "Details"**:
   - **Domain Names**: `certificados.transportespuno.gob.pe`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `161.132.47.99` (o `localhost`)
   - **Forward Port**: `7070`
   - **Cache Assets**: ✅ (activar)
   - **Block Common Exploits**: ✅ (activar)
   - **Websockets Support**: ✅ (activar)

3. **Configurar pestaña "SSL"** (opcional pero recomendado):
   - **SSL Certificate**: `Request a new SSL Certificate`
   - **Force SSL**: ✅ (activar)
   - **HTTP/2 Support**: ✅ (activar)
   - **HSTS Enabled**: ✅ (activar)
   - **Email**: tu-email@transportespuno.gob.pe

4. **Configurar pestaña "Advanced"** (opcional):
   ```nginx
   # Configuración adicional para Django
   proxy_set_header Host $host;
   proxy_set_header X-Real-IP $remote_addr;
   proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
   proxy_set_header X-Forwarded-Proto $scheme;
   
   # Para archivos estáticos grandes
   client_max_body_size 100M;
   ```

5. **Guardar**: Click en `Save`

---

## 🧪 VERIFICACIÓN

### Después de configurar NPM:

```bash
# 1. Probar el dominio (debería funcionar)
curl -I http://certificados.transportespuno.gob.pe

# 2. Probar HTTPS (si configuraste SSL)
curl -I https://certificados.transportespuno.gob.pe

# 3. Verificar que el puerto 7070 sigue funcionando internamente
curl -I http://localhost:7070/consulta/
```

---

## 🎯 CONFIGURACIÓN ALTERNATIVA (Si no tienes acceso a NPM)

### Opción 1: Cambiar puerto de la aplicación a 80
```bash
# Cambiar puerto en docker-compose
sed -i 's/7070:80/80:80/g' docker-compose.prod.yml

# Detener NPM temporalmente
docker stop nginx-proxy-app-1

# Reiniciar aplicación
docker compose -f docker-compose.prod.yml --env-file .env.production restart nginx
```

### Opción 2: Usar subdominio
Si no puedes configurar NPM, usar un subdominio como:
- `certificados-app.transportespuno.gob.pe:7070`

---

## 📝 CONFIGURACIÓN RECOMENDADA EN NPM

```
Domain: certificados.transportespuno.gob.pe
Forward to: 161.132.47.99:7070
SSL: Let's Encrypt (automático)
Force SSL: Sí
HTTP/2: Sí
```

---

## 🚨 IMPORTANTE

1. **Credenciales NPM**: Cambia las credenciales por defecto
2. **SSL**: Configura certificado SSL para HTTPS
3. **Firewall**: Asegúrate que el puerto 7070 esté accesible internamente
4. **DNS**: Verifica que el dominio apunte correctamente a la IP

---

## ✅ RESULTADO ESPERADO

Después de la configuración:
- ✅ `http://certificados.transportespuno.gob.pe` → Aplicación
- ✅ `https://certificados.transportespuno.gob.pe` → Aplicación (con SSL)
- ✅ Certificado SSL automático
- ✅ Redirección HTTP → HTTPS